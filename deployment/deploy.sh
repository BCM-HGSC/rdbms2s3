#!/bin/bash

# Determine environment from hostname
if [[ $HOSTNAME =~ "stg" ]]
then
    environment="staging"
elif [[ $HOSTNAME =~ "prd" ]]
then
    environment="prod"
else
    environment="dev"
fi

# rdbms2s3 deployment path
rdbms2s3_install_dir="/space1/deploy/${environment}/rdbms2s3"

# python3 conda environment for hgsc_rdbms2s3 scripts in rdbms2s3 deployment
conda_install="/hgsc_software/miniconda/miniconda3/bin/conda"
hgsc_rdbms2s3_conda_env="/space1/deploy/${environment}/conda/rdbms2s3"

# Usage function (and exit)
usage() {
  cat <<END
Usage: $0 [-h] [-c configfile.sh] [-t refspec] [-k] [-f] [-v]
    -h                  Display this help screen
    -t <refspec>        Optional git reference (tag, branch, SHA) to use for reset
                        If omitted, will construct from \$environment and "_cron"
    -k                  Keep all previous conda deployment directories
    -f                  Force: Perform all operations without (much) checking.
    -v                  Verbose: sets bash shopt of -x
Environment:
    conda_install             required path to find conda for env setup
    rdbms2s3_install_dir       required path to find git repo
    hgsc_rdbms2s3_conda_env    required path to create conda environment
END

  exit 5
}

# Reinstall conda environment
redeploy_conda_env() {
    set -e

    source ${conda_env_setup}
    [[ -d ${hgsc_rdbms2s3_conda_env} ]] && mv ${hgsc_rdbms2s3_conda_env} ${hgsc_rdbms2s3_conda_env}.$(date +%F)
    conda create -y --prefix $hgsc_rdbms2s3_conda_env pip
    conda activate $hgsc_rdbms2s3_conda_env
    pip install -U ${rdbms2s3_install_dir}
    conda deactivate
    set +e
}

update_git_repo() {
    UPDATE_CONDA=${FORCE:-0}
    UPDATE_REPO=${FORCE:-0}

    GIT="git --git-dir=${rdbms2s3_install_dir}/.git --work-tree=${rdbms2s3_install_dir}"

    ${GIT} fetch

    # Determine if changes happened in python3 project
    if ! ${GIT} diff --quiet origin/${git_target_ref} -- src
    then
        UPDATE_CONDA=1
        UPDATE_REPO=1
    # Determine if changes happened generally
    elif ! ${GIT} diff --quiet origin/${git_target_ref}
    then
        UPDATE_REPO=1
    fi

    # Reset (not checkout or pull) latest in branch
    [ $UPDATE_REPO -eq 1 ] && ${GIT} reset --hard origin/${git_target_ref}
    [ $UPDATE_CONDA -eq 1 ] && redeploy_conda_env
}

remove_old_conda_dirs()
{
    if [ -z "${KEEP_OLD_CONDA_DIRS}" ]; then
        local conda_install_dir="$(dirname ${hgsc_rdbms2s3_conda_env})"
        local conda_install_base="$(basename ${hgsc_rdbms2s3_conda_env})"

        # Find previous conda deployment directories in $conda_install_dir and
        # remove all but latest 3 directories, ordered numerically by date
        find ${conda_install_dir} -maxdepth 1 -name "${conda_install_base}.*" |
            sort -nr |
            sed -e '1,3d' |
            xargs -r rm -fr
    fi
}

# Process arguments
while getopts "c:fhknt:v" options
do
    case "${options}" in
        c)
            [ -f ${OPTARG} ] && source ${OPTARG}
            CONFIG=1
            ;;
        f)
            FORCE=1
            ;;
        h)
            usage
            ;;
        k)
            KEEP_OLD_CONDA_DIRS=1
            ;;
        t)
            git_target_ref=${OPTARG}
            ;;
        v)
            set -x
            ;;
    esac
done

# Variables and sanity checks

# Make assumptions from environment (but respect overrides)
if [[ -z ${git_target_ref} ]]
then
    case "${environment}" in
        prod)
            git_target_ref="production_cron"
            ;;
        staging)
            git_target_ref="staging_cron"
            ;;
        dev)
            git_target_ref="main"
            ;;
    esac
fi

# After two chances to read config file, check for vars we expect to be filled in
[[ ! -d ${rdbms2s3_install_dir}/.git ]] && echo 'ERROR: environment variable "rdbms2s3_install_dir" must point at a git repo clone' && usage

# Only check parent directory of conda environment exists in case we need to make a new one.
[[ ! -d $(dirname ${hgsc_rdbms2s3_conda_env}) ]] && echo 'ERROR: environment variable "hgsc_rdbms2s3_conda_env" must point at a conda environment' && usage
# Artifact of run_common.sh, we want to use the profile setup script, but the only var we have is the conda python script
[[ ! -f ${conda_install} ]] && echo 'ERROR: environment variable "conda_install" must point at a "conda" script' && usage
conda_env_setup=$(dirname $(dirname ${conda_install} ))/etc/profile.d/conda.sh
# I could be wrong here....
[[ ! -f ${conda_env_setup} ]] && echo 'ERROR: Bad assumption made in script that conda will provide a profile setup script at ${conda_env_setup}' && usage

update_git_repo
remove_old_conda_dirs
