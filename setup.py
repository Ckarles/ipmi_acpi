from setuptools import setup

setup(
    name='ipmi_acpi',
    version='0.1',
    py_modules=['ipmi_acpi'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        ipmi_acpi=sample.ipmi_acpi:cli
    '''
)
