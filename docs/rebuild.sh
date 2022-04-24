parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
poetry run sphinx-apidoc -f -o source ../formpy && poetry run make html