import os
import xacro

from launch_ros.actions import Node
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription


def generate_launch_description():
    # Launch Arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default=True)

    littlebot_gazebo_path = os.path.join(
        get_package_share_directory('littlebot_gazebo'))

    littlebot_description_path = os.path.join(
        get_package_share_directory('littlebot_description'))

    ros_gz_sim_path = os.path.join(
        get_package_share_directory('ros_gz_sim'))

    # World file name
    world_file = os.path.join(littlebot_gazebo_path, 'worlds', 'floor.sdf')

    xacro_file = os.path.join(littlebot_description_path,
                              'urdf',
                              'littlebot_description.urdf.xacro')

    doc = xacro.parse(open(xacro_file))
    xacro.process_doc(doc)
    params = {'robot_description': doc.toxml()}

    # print(params)

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params],
    )

    ignition_spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-string', doc.toxml(),
                   '-name', 'littlebot',
                   '-x', '0.0',
                   '-y', '0.0',
                   '-z', '1.0',
                   '-R', '0.0',
                   '-P', '0.0',
                   '-Y', '0.0',
                   '-allow_renaming', 'true'],
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
        ],
        output='screen'
    )

    return LaunchDescription([
        # Launch gazebo environment
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ros_gz_sim_path, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': '-r {}'.format(world_file)}.items(),
        ),
        node_robot_state_publisher,
        bridge,
        ignition_spawn_entity,
        # Launch Arguments
        DeclareLaunchArgument(
            'use_sim_time',
            default_value=use_sim_time,
            description='If true, use simulated clock'),
    ])
