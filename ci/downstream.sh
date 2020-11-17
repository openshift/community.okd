#!/bin/bash -e

# Script to dual-home the upstream and downstream Collection in a single repo
#
#   This script will build or test a downstream collection, removing any
#   upstream components that will not ship in the downstream release
#
#   NOTES:
#       - All functions are prefixed with f_ so it's obvious where they come
#         from when in use throughout the script

DOWNSTREAM_VERSION="1.0.1"
KEEP_DOWNSTREAM_TMPDIR="${KEEP_DOWNSTREAM_TMPDIR:-''}"
_build_dir=""

f_log_info()
{
    printf "%s:LOG:INFO: %s\n" "${0}" "${1}"
}

f_show_help()
{
    printf "Usage: downstream.sh [OPTION]\n"
    printf "\t-s\t\tCreate a temporary downstream release and perform sanity tests.\n"
    printf "\t-i\t\tCreate a temporary downstream release and perform integration tests.\n"
    printf "\t-m\t\tCreate a temporary downstream release and perform molecule tests.\n"
    printf "\t-b\t\tCreate a downstream release and stage for release.\n"
    printf "\t-r\t\tCreate a downstream release and publish release.\n"
}

f_text_sub()
{
    # Switch FQCN and dependent components
    OKD_sed_files="${_build_dir}/README.md ${_build_dir}/CHANGELOG.rst ${_build_dir}/changelogs/config.yaml ${_build_dir}/ci/downstream.sh ${_build_dir}/galaxy.yml"
    for okd_file in ${OKD_sed_files[@]}; do sed -i.bak "s/OKD/OpenShift/g" "${okd_file}"; done

    sed -i.bak "s/============================/==================================/" "${_build_dir}/CHANGELOG.rst"
    sed -i.bak "s/Ansible Galaxy/Automation Hub/" "${_build_dir}/README.md"
    sed -i.bak "s/community-okd/redhat-openshift/" "${_build_dir}/Makefile"
    sed -i.bak "s/community\/okd/redhat\/openshift/" "${_build_dir}/Makefile"
    sed -i.bak "s/^VERSION\:/VERSION: ${DOWNSTREAM_VERSION}/" "${_build_dir}/Makefile"
    sed -i.bak "s/name\:.*$/name: openshift/" "${_build_dir}/galaxy.yml"
    sed -i.bak "s/namespace\:.*$/namespace: redhat/" "${_build_dir}/galaxy.yml"
    sed -i.bak "s/Kubernetes/OpenShift/g" "${_build_dir}/galaxy.yml"
    sed -i.bak "s/^version\:.*$/version: ${DOWNSTREAM_VERSION}/" "${_build_dir}/galaxy.yml"
    sed -i.bak "/STARTREMOVE/,/ENDREMOVE/d" "${_build_dir}/README.md"

    find "${_build_dir}" -type f -exec sed -i.bak "s/community\.okd/redhat\.openshift/g" {} \;
    find "${_build_dir}" -type f -name "*.bak" -delete
}

f_prep()
{
    f_log_info "${FUNCNAME[0]}"
    # Array of excluded files from downstream build (relative path)
    _file_exclude=(
    )

    # Files to copy downstream (relative repo root dir path)
    _file_manifest=(
        CHANGELOG.rst
        galaxy.yml
        LICENSE
        README.md
        Makefile
        setup.cfg
        .yamllint
    )

    # Directories to recursively copy downstream (relative repo root dir path)
    _dir_manifest=(
        changelogs
        ci
        meta
        molecule
        plugins
        tests
    )

    # Modules with inherited doc fragments from kubernetes.core that need
    # rendering to deal with Galaxy/AH lack of functionality.
    _doc_fragment_modules=(
        k8s
        openshift_process
        openshift_route
    )


    # Temp build dir
    _tmp_dir=$(mktemp -d)
    _start_dir="${PWD}"
    _build_dir="${_tmp_dir}/ansible_collections/redhat/openshift"
    mkdir -p "${_build_dir}"
}


f_cleanup()
{
    f_log_info "${FUNCNAME[0]}"
    if [[ -n "${_build_dir}" ]]; then
        if [[ -n ${KEEP_DOWNSTREAM_TMPDIR} ]]; then
            if [[ -d ${_build_dir} ]]; then
                rm -fr "${_build_dir}"
            fi
        fi
    else
        exit 0
    fi
}

# Exit and handle cleanup processes if needed
f_exit()
{
    f_cleanup
    exit "$0"
}

f_create_collection_dir_structure()
{
    f_log_info "${FUNCNAME[0]}"
    # Create the Collection
    for f_name in "${_file_manifest[@]}";
    do
        cp "./${f_name}" "${_build_dir}/${f_name}"
    done
    for d_name in "${_dir_manifest[@]}";
    do
        cp -r "./${d_name}" "${_build_dir}/${d_name}"
    done
    if [ -n "${_file_exclude:-}" ]; then
        for exclude_file in "${_file_exclude[@]}";
        do
            if [[ -f "${_build_dir}/${exclude_file}" ]]; then
                rm -f "${_build_dir}/${exclude_file}"
            fi
        done
    fi
}

f_handle_doc_fragments_workaround()
{
    f_log_info "${FUNCNAME[0]}"
    local install_collections_dir="${_build_dir}/collections/"
    local temp_fragments_json="${_tmp_dir}/fragments.json"
    local temp_start="${_tmp_dir}/startfile.txt"
    local temp_end="${_tmp_dir}/endfile.txt"
    local rendered_fragments="./rendereddocfragments.txt"

    # Build the collection, export docs, render them, stitch it all back together
    pushd "${_build_dir}" || return
        ansible-galaxy collection build
        ansible-galaxy collection install -p "${install_collections_dir}" ./*.tar.gz
        rm ./*.tar.gz
        for doc_fragment_mod in "${_doc_fragment_modules[@]}"
        do
            local module_py="plugins/modules/${doc_fragment_mod}.py"
            f_log_info "Processing doc fragments for ${module_py}"
            ANSIBLE_COLLECTIONS_PATH="${install_collections_dir}" \
            ANSIBLE_COLLECTIONS_PATHS="${ANSIBLE_COLLECTIONS_PATH}:${install_collections_dir}" \
                ansible-doc -j "redhat.openshift.${doc_fragment_mod}" > "${temp_fragments_json}"
            # FIXME: Check Python interpreter from environment variable to work with prow
            if [ -e /usr/bin/python3.6 ]; then
                PYTHON="/usr/bin/python3.6"
            else
                PYTHON="python"
            fi
            "${PYTHON}" "${_start_dir}/ci/downstream_fragments.py" "redhat.openshift.${doc_fragment_mod}" "${temp_fragments_json}"
            sed -n '/STARTREMOVE/q;p' "${module_py}" > "${temp_start}"
            sed '0,/ENDREMOVE/d' "${module_py}" > "${temp_end}"
            cat "${temp_start}" "${rendered_fragments}" "${temp_end}" > "${module_py}"
            cat "${module_py}"
        done
        rm -f "${rendered_fragments}"
        rm -fr "${install_collections_dir}"
    popd

}

f_install_kubernetes_core()
{
    f_log_info "${FUNCNAME[0]}"
    local install_collections_dir="${_tmp_dir}/ansible_collections"

    pushd "${_tmp_dir}"
        ansible-galaxy collection install -p "${install_collections_dir}" kubernetes.core
    popd
}


f_copy_collection_to_working_dir()
{
    f_log_info "${FUNCNAME[0]}"
    # Copy the Collection build result into original working dir
    cp "${_build_dir}"/*.tar.gz ./
}

f_common_steps()
{
    f_log_info "${FUNCNAME[0]}"
    f_prep
    f_create_collection_dir_structure
    f_text_sub
    f_handle_doc_fragments_workaround
}

# Run the test sanity scanerio
f_test_sanity_option()
{
    f_log_info "${FUNCNAME[0]}"
    f_common_steps
    f_install_kubernetes_core
    pushd "${_build_dir}" || return
        ansible-galaxy collection build
        f_log_info "SANITY TEST PWD: ${PWD}"
        ## Can't do this because the upstream kubernetes.core dependency logic
        ## is bound as a Makefile dep to the test-sanity target
        #SANITY_TEST_ARGS="--docker --color --python 3.6" make test-sanity
        # Run tests in docker if available, venv otherwise
        if command -v docker &> /dev/null
        then
            ansible-test sanity --docker -v --exclude ci/ --color --python 3.6
        else
            ansible-test sanity --venv -v --exclude ci/ --color --python 3.6
        fi
    popd || return
    f_cleanup
}

# Run the test integration
f_test_integration_option()
{
    f_log_info "${FUNCNAME[0]}"
    f_common_steps
    f_install_kubernetes_core
    pushd "${_build_dir}" || return
        f_log_info "INTEGRATION TEST WD: ${PWD}"
        OVERRIDE_COLLECTION_PATH="${_tmp_dir}" molecule test
    popd || return
    f_cleanup
}

# Run the build scanerio
f_build_option()
{
    f_log_info "${FUNCNAME[0]}"
    f_common_steps
    pushd "${_build_dir}" || return
        f_log_info "BUILD WD: ${PWD}"
        # FIXME
        #   This doesn't work because we end up either recursively curl'ing
        #   kubernetes.core and redoing the text replacement over and over
        #
        # make build
        ansible-galaxy collection build

    popd || return
    f_copy_collection_to_working_dir
    f_cleanup
}

# If no options are passed, display usage and exit
if [[ "${#}" -eq "0" ]]; then
    f_show_help
    f_exit 0
fi

# Handle options
while getopts ":sirb" option
do
  case $option in
    s)
        f_test_sanity_option
        ;;
    i)
        f_test_integration_option
        ;;
    r)
        f_release_option
        ;;
    b)
        f_build_option
        ;;
    *)
        printf "ERROR: Unimplemented option chosen.\n"
        f_show_help
        f_exit 1
        ;;   # Default.
  esac
done

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
