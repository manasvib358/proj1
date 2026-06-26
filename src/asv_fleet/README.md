# asv_fleet

Three-robot autonomous surface vehicle (ASV) fleet for lake waste
detection. Built for **ROS2 Humble + Gazebo Classic (gazebo11)** on
Ubuntu 22.04.

What this package actually does differently from a "model just sitting
in the world file":

- Each robot is a real `xacro`-generated URDF with a proper
  `base_link` → `mast_link` → `lidar_link` and `base_link` →
  `camera_link` → `camera_optical_link` joint tree.
- Robots are **spawned** via `spawn_entity.py` reading from
  `robot_state_publisher`'s `robot_description` topic -- not baked
  statically into the world SDF -- so Gazebo treats them as real,
  independently controllable entities.
- Movement, camera, and lidar are wired through actual `gazebo_ros`
  sensor/control plugins, publishing real ROS2 topics.

## 1. Install dependencies

```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-xacro \
                  ros-humble-robot-state-publisher ros-humble-joint-state-publisher
# Only needed once you get to AprilTag detection (step 5):
sudo apt install ros-humble-apriltag-ros
```

## 2. Build

Copy (or unzip) this `asv_fleet/` folder into your workspace's `src/`,
e.g. `~/ros2_ws/src/asv_fleet`, then:

```bash
cd ~/ros2_ws
colcon build --packages-select asv_fleet
source install/setup.bash
```

`source` that `setup.bash` in every new terminal you use below.

## 3. Test with one robot first

Don't jump straight to all three -- debug one boat first, it's much
easier to read the terminal output:

```bash
ros2 launch asv_fleet spawn_single_asv.launch.py
```

You should see Gazebo open with the lake world and **one red boat
sitting on the water surface**. If your machine has an Intel
integrated GPU and Gazebo fails to render or crashes on startup, run
instead:

```bash
LIBGL_ALWAYS_SOFTWARE=1 MESA_GL_VERSION_OVERRIDE=3.3 ros2 launch asv_fleet spawn_single_asv.launch.py
```

Check it's alive, in another terminal:

```bash
ros2 topic list                      # should show /red_asv/cmd_vel, /red_asv/scan, etc.
ros2 topic echo /red_asv/scan --once # lidar should be returning ranges
```

Drive it manually:

```bash
ros2 topic pub -r 10 /red_asv/cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {z: 0.2}}"
```

The boat should glide forward and curve -- if it doesn't move, see
**Troubleshooting** below.

## 4. Spawn the full fleet

```bash
ros2 launch asv_fleet spawn_fleet.launch.py
```

Three boats (red, green, blue) spawn at different starting points so
they don't overlap. Each has its own namespace:

| Topic                              | Type                          | What it is              |
|-------------------------------------|--------------------------------|--------------------------|
| `/<name>/cmd_vel`                   | `geometry_msgs/Twist`          | drive command            |
| `/<name>/odom`                      | `nav_msgs/Odometry`            | position/velocity        |
| `/<name>/camera/image_raw`          | `sensor_msgs/Image`            | RGB camera feed          |
| `/<name>/camera/camera_info`        | `sensor_msgs/CameraInfo`       | camera calibration       |
| `/<name>/scan`                      | `sensor_msgs/LaserScan`        | 2D lidar                 |

`<name>` is `red_asv`, `green_asv`, or `blue_asv`.

View a camera feed:

```bash
ros2 run rqt_image_view rqt_image_view /red_asv/camera/image_raw
```

## 5. AprilTag waste detection

The lake world includes three floating waste markers, each printed
with a real `tag36h11` AprilTag (IDs 0, 1, 2) -- the actual bit
pattern, not a placeholder image, so a real AprilTag detector can read
them off the simulated camera.

```bash
ros2 launch asv_fleet apriltag_detection.launch.py
```

This starts one `apriltag_ros` detector per robot, subscribed to that
robot's own camera. Detections publish to `/<name>/tag_detections`.

**apriltag_ros's parameter format has changed across releases** -- if
this launch file errors about unrecognized parameters, compare
`config/tags.yaml` against the example config under
`/opt/ros/humble/share/apriltag_ros/` and adjust the keys to match.

## 6. Autonomous "find and approach the waste" behaviour

A minimal proportional-control node: if a tag is visible, steer toward
it and move forward; if not, spin slowly to search.

```bash
ros2 launch asv_fleet fleet_autonomy.launch.py
```

Run steps 4, 5, and 6 together (three terminals) and you should see
all three boats spin in place until a tag enters their camera view,
then curve toward it.

This is intentionally simple -- single nearest-visible-tag chase, no
obstacle avoidance, no path planning -- so you can read
`scripts/waste_seek_node.py` top to bottom and understand exactly what
it does before building on it (e.g. adding lidar-based obstacle
avoidance, or splitting up which robot chases which tag).

## Troubleshooting

**Boat doesn't move when you publish to cmd_vel** -- check
`ros2 topic list` for `/<name>/cmd_vel` existing and check
`ros2 node info` on the gazebo node to confirm
`libgazebo_ros_planar_move.so` loaded without errors in the terminal
where you ran the launch file. SDF plugin load failures print there,
not as a ROS2 error.

**Boat sinks / falls through the water** -- the hull link needs
`<kinematic>true</kinematic>` (already set in `asv_macro.xacro`,
`<gazebo reference="${robot_name}_base_link">`). If you've modified
the xacro and lost it, gravity will pull the hull straight down.

**Three robots' TF all show the same frame names** -- every link in
`asv_macro.xacro` is prefixed with `${robot_name}_` specifically to
avoid this; if you add new links, prefix them too.

**Gazebo doesn't render / black screen / segfault on an Intel iGPU** --
launch with `LIBGL_ALWAYS_SOFTWARE=1 MESA_GL_VERSION_OVERRIDE=3.3`
(see step 3).

**`apriltag_node` executable not found** -- run
`ros2 pkg executables apriltag_ros` to see the actual executable name
shipped with your installed version, and update
`launch/apriltag_detection.launch.py` accordingly.

## What's deliberately simplified (and why)

- **Kinematic floating, not true buoyancy physics.** Real buoyancy
  (Gazebo's `BuoyancyPlugin`) needs per-link volume/center-of-buoyancy
  tuning and tends to oscillate/destabilize for beginners. Since this
  project is about *perception and detection*, not hydrodynamics, the
  hull is locked to water height and driven kinematically instead --
  reliable, and looks correct from outside.
- **Holonomic-ish movement.** `gazebo_ros_planar_move` can technically
  take `linear.y` (sideways) commands, which a real boat can't do. For
  realistic boat behaviour, only ever publish `linear.x` and
  `angular.z` from your autonomy code (which is exactly what
  `waste_seek_node.py` does).
- **Box hull, not a mesh.** Easy to swap later: replace the `<box>`
  geometry in `asv_macro.xacro`'s hull `<visual>`/`<collision>` with a
  `<mesh>` pointing at a `.dae`/`.stl` boat model if you want it to
  look nicer for a demo video.

## Next milestones (not yet in this package)

- Obstacle avoidance using the lidar `/scan` topic
- A proper task allocator so the three boats split up the lake instead
  of all converging on the same tag
- Swapping the simple proportional steering for a PID or pure-pursuit
  controller
