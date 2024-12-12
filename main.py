import argparse
import urllib.request
import gzip
import re
import sys
from collections import deque

def parse_arguments():
    parser = argparse.ArgumentParser(description='Dependency graph visualizer')
    parser.add_argument('--graphviz-path', required=True, help='Path to the graph visualization program')
    parser.add_argument('--package-name', required=True, help='Name of the package to analyze')
    parser.add_argument('--output-file', required=True, help='Path to the result file in code')
    parser.add_argument('--repo-url', required=True, help='URL of the repository')
    return parser.parse_args()

def download_and_parse_packages(repo_url):
    print("Загрузка и разбор пакетов из репозитория...")
    try:
        with urllib.request.urlopen(repo_url, timeout=30) as response:  # Увеличен таймаут до 30 секунд
            compressed_data = response.read()
    except Exception as e:
        print(f"Ошибка загрузки файла Packages.gz: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        decompressed_data = gzip.decompress(compressed_data)
    except Exception as e:
        print(f"Ошибка распаковки файла Packages.gz: {e}", file=sys.stderr)
        sys.exit(1)

    packages_dict = parse_packages_file(decompressed_data.decode('utf-8'))
    print("Пакеты успешно загружены и разобраны.")
    return packages_dict

def parse_packages_file(packages_text):
    packages_dict = {}
    current_package = {}
    last_key = None
    for line in packages_text.split('\n'):
        if line.startswith(' ') or line.startswith('\t'):
            if last_key:
                current_package[last_key] += ' ' + line.strip()
        elif not line.strip():
            if 'Package' in current_package:
                package_name = current_package['Package']
                packages_dict[package_name] = current_package
            current_package = {}
            last_key = None
        else:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                current_package[key] = value
                last_key = key

    if 'Package' in current_package:
        package_name = current_package['Package']
        packages_dict[package_name] = current_package
    return packages_dict

def parse_dependencies(depends_str):
    dependencies = []
    if not depends_str:
        return dependencies

    dep_list = depends_str.split(',')
    for dep in dep_list:
        dep = dep.strip()
        alternatives = dep.split('|')
        for alt in alternatives:
            alt = alt.strip()
            alt = re.sub(r'\s*\(.*?\)', '', alt)
            if alt:
                dependencies.append(alt)
    return dependencies

def build_dependency_graph(package_name, packages_dict):
    print(f"Строим граф зависимостей для пакета: {package_name}")
    dependency_graph = set()
    visited = set()
    queue = deque()
    queue.append(package_name)
    visited.add(package_name)

    while queue:
        current_pkg = queue.popleft()
        if current_pkg not in packages_dict:
            continue
        pkg_info = packages_dict[current_pkg]
        depends = pkg_info.get('Depends', '')
        dependencies = parse_dependencies(depends)
        for dep in dependencies:
            dependency_graph.add((current_pkg, dep))
            if dep not in visited:
                visited.add(dep)
                queue.append(dep)
    print(f"Граф зависимостей для пакета {package_name} построен.")
    return dependency_graph

def generate_dot_code(dependency_graph):
    print("Генерация DOT-кода для визуализации графа...")
    dot = 'digraph dependencies {\n'
    for src, dst in sorted(dependency_graph):
        dot += f'    "{src}" -> "{dst}";\n'
    dot += '}\n'
    print("DOT-код успешно сгенерирован.")
    return dot

def main():
    args = parse_arguments()
    print("Аргументы командной строки успешно разобраны.")

    packages_dict = download_and_parse_packages(args.repo_url)

    dependency_graph = build_dependency_graph(args.package_name, packages_dict)

    dot_code = generate_dot_code(dependency_graph)

    with open(args.output_file, 'w') as f:
        f.write(dot_code)
    print(f"DOT-код записан в файл {args.output_file}.")

    # Чтение и вывод файла в консоль
    print("Вывод содержимого файла в консоль:")
    try:
        with open(args.output_file, 'r') as f:
            for line in f:
                print(line.strip())
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
