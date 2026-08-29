from __future__ import annotations

from .models import Rule


RULES: tuple[Rule, ...] = (
    Rule(
        identifier="ros2_missing_runtime_dependency",
        title="ROS2 package dependency is missing or not declared",
        root_cause=(
            "A node or launch file imports/executes a package that is not installed, "
            "not built, or not declared in package.xml."
        ),
        fix=(
            "Install the missing dependency or add it to package.xml, then run "
            "rosdep install, rebuild with colcon, and source the workspace."
        ),
        verification=(
            "rosdep install --from-paths src --ignore-src -r -y",
            "colcon build --symlink-install",
            "source install/setup.bash",
            "ros2 pkg prefix <missing_package>",
        ),
        confirm_patterns=(
            "PackageNotFoundError",
            "package .* not found",
            "No module named",
            "Could not find a package configuration file provided by",
        ),
        context_patterns=("package.xml", "find_package", "exec_depend", "depend>", "import "),
        ros_versions=("ros2",),
    ),
    Rule(
        identifier="ros2_namespace_or_topic_mismatch",
        title="ROS2 topic or namespace mismatch",
        root_cause=(
            "Publisher and subscriber names do not resolve to the same fully qualified "
            "topic, often because remaps, namespaces, or leading slashes differ."
        ),
        fix=(
            "Normalize topic names and remaps across launch files and node code. Verify "
            "with ros2 topic list, ros2 node info, and a minimal pub/sub test."
        ),
        verification=(
            "ros2 node list",
            "ros2 node info <node_name>",
            "ros2 topic list -t",
            "ros2 topic echo <expected_topic> --once",
        ),
        confirm_patterns=(
            "waiting for message",
            "no publishers",
            "no subscribers",
            "topic .* not available",
            "Timed out waiting for transform",
        ),
        context_patterns=("remap", "namespace", "topic", "create_subscription", "create_publisher"),
        ros_versions=("ros2",),
    ),
    Rule(
        identifier="workspace_not_sourced",
        title="Workspace or ROS environment was not sourced",
        root_cause=(
            "The shell environment cannot see ROS packages because setup.bash/local_setup.bash "
            "was not sourced, or ROS_PACKAGE_PATH/AMENT_PREFIX_PATH points at the wrong workspace."
        ),
        fix=(
            "Source the correct ROS distribution and workspace setup file in the active shell, "
            "then rerun package discovery before launching."
        ),
        verification=(
            "echo $ROS_DISTRO",
            "echo $AMENT_PREFIX_PATH",
            "echo $ROS_PACKAGE_PATH",
            "source /opt/ros/<distro>/setup.bash && source install/setup.bash",
        ),
        confirm_patterns=(
            "Resource not found",
            "package .* not found",
            "rospack.*Error",
        ),
        context_patterns=(
            "ROS_DISTRO=",
            "AMENT_PREFIX_PATH=",
            "ROS_PACKAGE_PATH=",
            "setup.bash",
            "local_setup.bash",
            "devel/setup.bash",
            "install/setup.bash",
        ),
    ),
    Rule(
        identifier="ros2_dds_domain_or_network_mismatch",
        title="ROS2 DDS domain or network discovery mismatch",
        root_cause=(
            "ROS2 nodes are running but cannot discover each other because ROS_DOMAIN_ID, "
            "RMW implementation, host networking, or multicast settings differ."
        ),
        fix=(
            "Align ROS_DOMAIN_ID and RMW_IMPLEMENTATION across processes, confirm multicast "
            "or container networking, and repeat topic discovery."
        ),
        verification=(
            "echo $ROS_DOMAIN_ID",
            "echo $RMW_IMPLEMENTATION",
            "ros2 doctor --report",
            "ros2 multicast receive",
        ),
        confirm_patterns=(
            "ROS_DOMAIN_ID",
            "RMW_IMPLEMENTATION",
            "no nodes discovered",
            "participant",
            "multicast",
        ),
        context_patterns=("docker", "network_mode", "CYCLONEDDS", "FASTRTPS", "domain"),
        ros_versions=("ros2",),
    ),
    Rule(
        identifier="tf_frame_or_clock_failure",
        title="TF frame, timestamp, or simulation clock failure",
        root_cause=(
            "Transforms are unavailable or rejected because frame IDs, timestamps, or "
            "use_sim_time settings are inconsistent."
        ),
        fix=(
            "Verify the TF tree, frame names, /clock publication, and use_sim_time on all "
            "nodes that consume transforms."
        ),
        verification=(
            "ros2 run tf2_tools view_frames",
            "ros2 topic echo /tf --once",
            "ros2 param get <node_name> use_sim_time",
            "ros2 topic echo /clock --once",
        ),
        confirm_patterns=(
            "Lookup would require extrapolation",
            "Invalid frame ID",
            "target_frame does not exist",
            "Timed out waiting for transform",
            "use_sim_time",
        ),
        context_patterns=("\\bbase_link\\b", "\\bmap\\b", "\\bodom\\b", "/clock", "robot_state_publisher", "static_transform_publisher"),
    ),
    Rule(
        identifier="ros1_master_or_uri_mismatch",
        title="ROS1 master URI or hostname mismatch",
        root_cause=(
            "ROS1 nodes cannot register or communicate because ROS_MASTER_URI, ROS_HOSTNAME, "
            "or ROS_IP is unset or points to the wrong host."
        ),
        fix=(
            "Start roscore if needed, align ROS_MASTER_URI and ROS_IP/ROS_HOSTNAME for every "
            "machine, and verify name resolution."
        ),
        verification=(
            "echo $ROS_MASTER_URI",
            "echo $ROS_IP",
            "rosnode list",
            "rostopic list",
        ),
        confirm_patterns=(
            "Unable to contact my own server",
            "Failed to contact master",
            "ROS_MASTER_URI",
            "roscore",
            "Connection refused",
        ),
        context_patterns=("ROS_HOSTNAME", "ROS_IP", "localhost", "master"),
        ros_versions=("ros1",),
    ),
    Rule(
        identifier="ros2_parameter_type_or_name_mismatch",
        title="ROS2 parameter name or type mismatch",
        root_cause=(
            "A launch file or YAML config provides a parameter name or value type that "
            "does not match what the node declares or expects."
        ),
        fix=(
            "Compare the node's declared parameters with YAML and launch inputs, correct "
            "the name or type, and verify with ros2 param describe/get."
        ),
        verification=(
            "ros2 param list <node_name>",
            "ros2 param describe <node_name> <parameter>",
            "ros2 param get <node_name> <parameter>",
            "ros2 launch <package> <launch_file> --show-args",
        ),
        confirm_patterns=(
            "InvalidParameterTypeException",
            "parameter .* has invalid type",
            "Parameter .* is not declared",
            "expected .* got",
            "failed to parse parameter",
        ),
        context_patterns=("ros__parameters", "DeclareParameter", "declare_parameter", "parameters=", "yaml"),
        ros_versions=("ros2",),
    ),
    Rule(
        identifier="ros2_missing_executable_entrypoint",
        title="ROS2 executable or entry point is missing",
        root_cause=(
            "The package exists, but the executable named by launch or ros2 run is not "
            "installed because setup.py/CMake install rules or console_scripts are wrong."
        ),
        fix=(
            "Add the missing console_scripts entry or install target, rebuild, source the "
            "install space, and confirm with ros2 pkg executables."
        ),
        verification=(
            "ros2 pkg executables <package>",
            "colcon build --symlink-install",
            "source install/setup.bash",
            "ros2 run <package> <executable>",
        ),
        confirm_patterns=(
            "executable .* not found",
            "No executable found",
            "libexec directory",
            "libexec directory .* does not exist",
            "ros2 run: error",
        ),
        context_patterns=("console_scripts", "entry_points", "install\\(", "executable=", "ament_python"),
        ros_versions=("ros2",),
    ),
    Rule(
        identifier="urdf_or_xacro_parse_failure",
        title="URDF or xacro parse failure",
        root_cause=(
            "Robot description generation fails because a URDF/xacro file has malformed "
            "XML, an undefined xacro property/macro, or an invalid mesh/reference path."
        ),
        fix=(
            "Run xacro directly, fix the reported XML/property/path issue, then restart "
            "robot_state_publisher and verify the robot_description parameter."
        ),
        verification=(
            "xacro <robot>.urdf.xacro",
            "check_urdf <robot>.urdf",
            "ros2 param get /robot_state_publisher robot_description",
            "ros2 run tf2_tools view_frames",
        ),
        confirm_patterns=(
            "xacro: error",
            "XML parsing error",
            "mismatched tag",
            "Undefined substitution argument",
            "No such file or directory: .*\\.stl",
            "No such file or directory: .*\\.dae",
        ),
        context_patterns=("robot_description", "<robot", "<xacro:", "mesh filename", "robot_state_publisher"),
    ),
    Rule(
        identifier="ros2_qos_policy_mismatch",
        title="ROS2 QoS policy mismatch",
        root_cause=(
            "A publisher and subscriber are on the same topic but use incompatible QoS "
            "policies such as reliability, durability, or history depth."
        ),
        fix=(
            "Align QoS profiles for the publisher and subscriber, then verify endpoint "
            "compatibility with ros2 topic info --verbose."
        ),
        verification=(
            "ros2 topic info <topic> --verbose",
            "ros2 topic echo <topic> --qos-reliability best_effort",
            "ros2 topic echo <topic> --qos-reliability reliable",
            "ros2 doctor --report",
        ),
        confirm_patterns=(
            "incompatible QoS",
            "QoS incompatibility",
            "reliability policy",
            "durability policy",
            "New publisher discovered.*incompatible",
        ),
        context_patterns=("QoSProfile", "BEST_EFFORT", "RELIABLE", "qos_profile", "SensorDataQoS"),
        ros_versions=("ros2",),
    ),
)
