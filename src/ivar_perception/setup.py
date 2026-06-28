from setuptools import find_packages, setup

package_name = 'ivar_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/tags.yaml']),
        ('share/' + package_name + '/launch', ['launch/apriltag.launch.py'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vibha17',
    maintainer_email='vibha17@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "apriltag_node = ivar_perception.AprilTag_detector:main", 
            "pose_estimator = ivar_perception.pose_estimator:main",
        ],
    },
)
