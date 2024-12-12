import unittest

from main import parse_dependencies, parse_packages_file, build_dependency_graph, generate_dot_code


class TestDependencyVisualizer(unittest.TestCase):

    def test_parse_dependencies(self):
        depends_str = 'libc6 (>= 2.2.5), libssl1.1 (>= 1.1.0), zlib1g (>= 1:1.1.4)'
        dependencies = parse_dependencies(depends_str)
        expected = ['libc6', 'libssl1.1', 'zlib1g']
        self.assertEqual(dependencies, expected)

    def test_parse_dependencies_with_alternatives(self):
        depends_str = 'libfoo | libbar, libbaz (>= 1.0)'
        dependencies = parse_dependencies(depends_str)
        expected = ['libfoo', 'libbar', 'libbaz']
        self.assertEqual(dependencies, expected)

    def test_parse_packages_file(self):
        packages_text = '''
Package: testpkg
Version: 1.0
Depends: libc6 (>= 2.2.5), libssl1.1 (>= 1.1.0)
Description: Test package

Package: libssl1.1
Version: 1.1.0
Depends: libc6 (>= 2.2.5)
Description: SSL library
'''
        packages_dict = parse_packages_file(packages_text)
        self.assertIn('testpkg', packages_dict)
        self.assertIn('libssl1.1', packages_dict)
        self.assertEqual(packages_dict['testpkg']['Depends'], 'libc6 (>= 2.2.5), libssl1.1 (>= 1.1.0)')
        self.assertEqual(packages_dict['libssl1.1']['Depends'], 'libc6 (>= 2.2.5)')

    def test_build_dependency_graph(self):
        packages_dict = {
            'testpkg': {'Depends': 'libc6 (>= 2.2.5), libssl1.1 (>= 1.1.0)'},
            'libc6': {'Depends': ''},
            'libssl1.1': {'Depends': 'libc6 (>= 2.2.5)'},
        }
        dependency_graph = build_dependency_graph('testpkg', packages_dict)
        expected_edges = {('testpkg', 'libc6'), ('testpkg', 'libssl1.1'), ('libssl1.1', 'libc6')}
        self.assertEqual(dependency_graph, expected_edges)

    def test_generate_dot_code(self):
        dependency_graph = {('testpkg', 'libc6'), ('testpkg', 'libssl1.1'), ('libssl1.1', 'libc6')}
        dot_code = generate_dot_code(dependency_graph)
        expected_dot = '''digraph dependencies {
    "libssl1.1" -> "libc6";
    "testpkg" -> "libc6";
    "testpkg" -> "libssl1.1";
}
'''
        self.assertEqual(dot_code.strip(), expected_dot.strip())

if __name__ == '__main__':
    unittest.main()
