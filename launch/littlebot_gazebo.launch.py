from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.event_handlers import OnProcessExit

ARGUMENTS = [
    DeclareLaunchArgument('world_path', default_value='',
                          description='The world path, by default is empty.world'),
]


def generate_launch_description():
    # Launch args
    world_path = LaunchConfiguration('world_path')

    config_littlebot_velocity_controller = PathJoinSubstitution(
        [FindPackageShare("littlebot_control"), "config", "control.yaml"]
    )

    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [FindPackageShare("littlebot_description"), "urdf", "littlebot_description.urdf.xacro"]
            ),
            " ",
            "name:=littlebot",
            " ",
            "prefix:=''",
            " ",
            "is_sim:=true",
            " ",
            "gazebo_controllers:=",
            config_littlebot_velocity_controller,
        ]
    )

    robot_description = {"robot_description": robot_description_content}

    spawn_littlebot_velocity_controller = Node(
        package='controller_manager',
        executable='spawner.py',
        arguments=['littlebot_velocity_controller', '-c', '/controller_manager'],
        output='screen',
    )

    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[{'use_sim_time': True}, robot_description],
    )

    spawn_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner.py',
        arguments=['joint_state_broadcaster', '-c', '/controller_manager'],
        output='screen',
    )

    # Make sure spawn_littlebot_velocity_controller starts after spawn_joint_state_broadcaster
    diffdrive_controller_spawn_callback = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_joint_state_broadcaster,
            on_exit=[spawn_littlebot_velocity_controller],
        )
    )

    # Gazebo server
    gzserver = ExecuteProcess(
        cmd=['gzserver', '--verbose'
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             world_path],
        output='screen',
    )

    # Gazebo client
    gzclient = ExecuteProcess(
        cmd=['gzclient', '--verbose'],
        output='screen',
        # condition=IfCondition(LaunchConfiguration('gui')),
    )

    spawn_robot = Node(
        package='gazebo_ros', 
        executable='spawn_entity.py',
        name='spawn_littlebot',
        arguments=['-entity', 'littlebot', '-topic', 'robot_description'],
        output='screen'
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(node_robot_state_publisher)
    ld.add_action(spawn_joint_state_broadcaster)
    ld.add_action(diffdrive_controller_spawn_callback)
    ld.add_action(gzserver)
    ld.add_action(gzclient)
    ld.add_action(spawn_robot)

    return ld