# 模型结构理解

Diffusion-Planner 把自动驾驶规划建模为条件轨迹生成问题。模型不是只预测 ego vehicle 的单条未来轨迹，而是联合生成自车和关键邻车的未来状态。

## 输入

主要输入包括:

- `ego_current_state`: 自车当前状态
- `neighbor_agents_past`: 周围车辆历史状态
- `lanes`: 局部车道向量地图
- `route_lanes`: 导航路线对应车道
- `static_objects`: 静态障碍物
- `lanes_speed_limit`: 车道限速
- `lanes_has_speed_limit`: 限速可用性 mask

## Encoder

Encoder 将多源场景信息编码成统一 token 表示:

- Agent encoder 处理邻车历史轨迹
- Static object encoder 处理静态障碍物
- Lane encoder 处理车道线、边界和交通灯信息
- Fusion encoder 用 self-attention 融合 agent、lane、static object token

当前验证中 encoder 输出形状为:

```text
(1, 107, 192)
```

含义:

- batch size: 1
- token 数: 32 agents + 5 static objects + 70 lanes = 107
- hidden dim: 192

## Decoder

Decoder 使用 DiT 风格结构，将扩散过程中的 noisy future trajectories 和 encoder context 融合，输出未来轨迹估计。

训练态输出:

```text
score_shape=(1, 11, 81, 4)
```

含义:

- batch size: 1
- 轨迹主体: 1 个 ego + 10 个 predicted neighbors = 11
- 时间点: 当前 1 帧 + 未来 80 帧 = 81
- 状态维度: x, y, cos(heading), sin(heading)

## 扩散规划直觉

自动驾驶未来轨迹具有多模态性。同一个场景中，合理行为可能包括减速、并线、绕行、等待等多种选择。Diffusion-Planner 将未来轨迹看作需要逐步去噪生成的对象，用场景上下文和路线信息作为条件，生成符合交通语义的未来轨迹。

## Classifier Guidance

项目还支持 classifier guidance。它可以在采样过程中加入额外约束，例如降低碰撞风险。直觉上，基础模型负责生成合理轨迹，guidance 负责把轨迹往更安全或更符合规则的方向推。

