# 智能制造数字孪生系统设计方案

> 工业 4.0 架构参考设计 | OPC UA + Python 数字孪生 + 强化学习调度 + Purdue 安全架构

---

## 专业术语表 (Glossary)

### OPC UA 与工业通信

| 术语 | 英文 | 定义 |
|------|------|------|
| OPC UA | Open Platform Communications Unified Architecture | IEC 62541 标准化的工业通信协议，支持信息建模、安全、发现 |
| NodeId | Node Identifier | OPC UA 地址空间中每个节点的唯一标识符，由 NamespaceIndex + Identifier 组成 |
| BrowsePath | Browse Path | 从根节点出发的层级路径，如 /Objects/Production/CNC_001/Status |
| Variable Node | Variable Node | 表示可读写数值的节点，如温度、速度、状态 |
| Object Node | Object Node | 包含其他节点（Variables/Methods/Objects）的容器节点 |
| Method Node | Method Node | 表示可调用的远程过程，如 StartMachine()、EmergencyStop() |
| ReferenceType | Reference Type | 节点间关系类型：HasComponent、Organizes、HasProperty 等 |
| Subscription | Subscription | 客户端订阅数据变化，服务器按采样间隔主动推送更新 |
| MonitoredItem | Monitored Item | 订阅中监控的单个节点，可设定死区(Deadband) |
| DataChangeFilter | Data Change Filter | 过滤规则：仅当值变化超过死区才推送通知 |
| SecureChannel | Secure Channel | OPC UA 安全通信信道，支持 Sign / SignAndEncrypt |
| Session | Session | 客户端与服务器的认证会话，包含用户凭证和权限 |
| Namespace | Namespace | 地址空间的逻辑分区，索引0为OPC UA核心，索引1+为用户定义 |
| Information Model | Information Model | 设备/系统的形式化描述，定义类型结构、实例和关系 |
| TypeDefinition | Type Definition | OPC UA 中定义对象类型的模板，如 CNCType → CNC_001 (实例) |

### 车间设备

| 术语 | 英文 | 定义 |
|------|------|------|
| CNC | Computer Numerical Control | 计算机数控机床，通过G代码控制刀具轨迹进行精密加工 |
| AGV | Automated Guided Vehicle | 自动导引车，沿预定路径运输物料 |
| 六轴机械臂 | Six-Axis Robot | 具有6个旋转关节的工业机器人，可到达工作空间内任意姿态 |
| MES | Manufacturing Execution System | 制造执行系统，管理从订单下达到产品完成的整个生产过程 |
| PLC | Programmable Logic Controller | 可编程逻辑控制器，用于实时控制设备执行 |
| SCADA | Supervisory Control And Data Acquisition | 监控与数据采集系统，HMI层的设备监控 |
| ERP | Enterprise Resource Planning | 企业资源计划系统，管理层级(生产计划、物料需求) |
| 立体仓库 | Automated Storage/Retrieval System (AS/RS) | 自动化存取系统，由堆垛机、货架和传送带组成 |
| 末端执行器 | End Effector | 机器人手腕末端的工具，如夹爪、吸盘、焊枪 |
| 刀具库 | Tool Magazine | CNC 自动换刀装置，存放多把刀具供加工中心调用 |

### 数字孪生

| 术语 | 英文 | 定义 |
|------|------|------|
| 数字孪生 | Digital Twin | 物理实体的虚拟镜像，包含几何、物理、行为和规则模型 |
| AAS | Asset Administration Shell | 资产管理壳(IEC 63278)，德国的数字孪生标准化框架 |
| 实时同步 | Real-Time Synchronization | 物理实体与数字孪生之间状态变化的双向同步 |
| 数据影子 | Data Shadow | 四个影子路径模型：Happy(正常)/Nil(空)/Empty(零)/Error(错误) |
| 状态机 | State Machine | 设备状态的有限状态模型，如空闲→运行→故障→维护 |
| 保真度 | Fidelity | 数字孪生对物理实体描述的精确程度 |

### 强化学习调度

| 术语 | 英文 | 定义 |
|------|------|------|
| DQN | Deep Q-Network | 深度Q网络，使用神经网络逼近Q值函数的强化学习算法 |
| 马尔可夫决策过程 | Markov Decision Process (MDP) | 由(S, A, P, R, γ)五元组定义的序列决策模型 |
| 状态空间 | State Space | 所有可能系统状态的集合，包括设备状态、队列长度、能耗 |
| 动作空间 | Action Space | 所有可能的调度动作，如分配任务到某台CNC |
| 奖励函数 | Reward Function | 标量反馈信号，引导智能体学会好的策略 |
| ε-贪心 | Epsilon-Greedy | 探索-利用策略，以概率ε随机选择动作，以1-ε选择最优动作 |
| 经验回放 | Experience Replay | 将(state, action, reward, next_state)元组存入记忆池，随机采样训练 |
| Target Network | Target Network | 定期从主网络同步的目标Q网络，稳定训练 |
| 双DQN | Double DQN | 解耦动作选择和Q值评估，减少Q值高估偏差 |
| 利用率 (Utilization) | / | 设备实际运行时间占总可用时间的比例 |
| 完工时间 (Makespan) | / | 一批任务从开始到全部完成的总时长 |

### 工业安全

| 术语 | 英文 | 定义 |
|------|------|------|
| Purdue 模型 | Purdue Enterprise Reference Architecture (PERA) | ISA-99/IEC 62443 定义的工控系统分层安全架构(0-5层) |
| OT | Operational Technology | 操作技术，用于监控和控制物理设备的硬件/软件 |
| IT | Information Technology | 信息技术，用于信息处理的企业计算系统 |
| DMZ | Demilitarized Zone | 隔离IT和OT网络的中介区，部署应用服务器和镜像数据库 |
| IDS | Intrusion Detection System | 入侵检测系统，监控网络流量中的异常模式 |
| 深度包检测 | Deep Packet Inspection (DPI) | 检查OPC UA数据包载荷内容 |
| 最小权限 | Least Privilege | 用户/进程仅被授予完成工作所需的最小权限 |
| 纵深防御 | Defense in Depth | 多层安全控制策略，没有单一防线是绝对可靠的 |
| IEC 62443 | / | 工业自动化和控制系统安全的国际标准体系 |
| 安全策略 | Security Policy | OPC UA的安全配置，包括None、Sign、SignAndEncrypt |

### 架构设计

| 术语 | 英文 | 定义 |
|------|------|------|
| ADR | Architecture Decision Record | 架构决策记录，文档化有意义的架构决策及上下文 |
| BR | Business Requirement | 业务需求编号，用于追溯与系统设计的关联 |
| 快乐路径 | Happy Path | 一切正常运行的理想数据流 |
| 零值路径 | Nil Path | 数据为nil/null的流路径 |
| 空值路径 | Empty Path | 数据为空容器(空数组、空对象)的流路径 |
| 错误路径 | Error Path | 发生异常或故障时的流路径 |
| FA | Fault Analysis | 故障场景分析，描述触发条件、影响、检测和恢复 |
| CQRS | Command Query Responsibility Segregation | 命令查询职责分离，读写操作走不同模型 |

**术语总数：52 | 覆盖领域：OPC UA通信(15) + 车间设备(10) + 数字孪生(7) + 强化学习调度(10) + 工业安全(7) + 架构设计(8) = ~47**

---

## 第一章：系统总览

### 1.1 虚构生产线定义

本设计方案围绕一条虚构的精密零件生产线展开。

```
                    ┌──────────────┐
                    │     ERP      │  Level 4
                    │  (SAP S/4)   │
                    └──────┬───────┘
                           │
                    ┌──────┴───────┐
                    │     MES      │  Level 3
                    │ (自研Python) │
                    └──────┬───────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────┴────┐      ┌─────┴─────┐     ┌─────┴─────┐
    │  SCADA  │      │ OPC UA    │     │    HMI    │
    │ (WinCC) │      │  Server   │     │ (Web UI)  │
    └────┬────┘      └─────┬─────┘     └───────────┘
         │                 │
    ┌────┴─────────────────┴────┐  Level 0-2
    │      Purdue Level 0-2     │
    │   ┌───────────────────┐   │
    │   │ 3x CNC 数控机床   │   │
    │   │ 2x 六轴机器人     │   │
    │   │ 1x AGV 自动导引车  │   │
    │   │ 1x 自动化立体仓库  │   │
    │   └───────────────────┘   │
    └──────────────────────────┘
```

**设备编号与参数：**

| 设备ID | 设备类型 | 型号(参考) | 关键参数 |
|--------|----------|-----------|----------|
| CNC-001 | 三轴CNC | DMG Mori CMX 600 | 主轴转速 12,000 rpm, 刀库 30 把, 精度 ±3μm |
| CNC-002 | 五轴CNC | DMG Mori DMU 50 | 主轴转速 15,000 rpm, 摆头 ±120°, 精度 ±2μm |
| CNC-003 | 三轴CNC | Mazak VCN-530C | 主轴转速 12,000 rpm, 刀库 30 把, 精度 ±5μm |
| ROB-001 | 六轴机器人 | FANUC M-20iD | 载荷 25kg, 臂展 1831mm, 重复精度 ±0.02mm |
| ROB-002 | 六轴机器人 | ABB IRB 2600 | 载荷 20kg, 臂展 1650mm, 重复精度 ±0.04mm |
| AGV-001 | 自动导引车 | 标准叉车式AGV | 载荷 1000kg, 导航精度 ±10mm, 电池 48V 200Ah |
| WH-001 | 自动化仓库 | 标准单元式 | 4排×10列×5层=200货位, 堆垛机1台 |

**产品定义：**

| 产品 | 零件名称 | 材质 | 关键工序 | 目标节拍 |
|------|---------|------|---------|---------|
| PART-A | 传动轴套 | 40Cr合金钢 | 车削(粗)→车削(精)→铣键槽→检测 | 4 min |
| PART-B | 连接法兰 | 7075铝合金 | 铣面→钻孔→攻丝→检测 | 3.5 min |

---

## 第二章：OPC UA 信息模型

### 2.1 地址空间命名规范

遵循 OPC UA Companion Specification 惯例：

```
命名空间索引:
  NS0 - OPC UA 核心 (http://opcfoundation.org/UA/)
  NS1 - 本系统 (http://smds.local/UA/)
  NS2 - 设备类型 (http://smds.local/UA/DeviceTypes/)

NodeId 格式: ns=<namespace>;s=<string_identifier>
BrowsePath 格式: /Objects/<DeviceType>/<DeviceID>/<Component>/<Variable>
```

### 2.2 类型定义体系

```
BaseObjectType (NS0)
 ├── DeviceType (NS2)                    ┌─→ CNCType
 │    ├── CNCMachineType (NS2)         ──┤
 │    ├── RobotType (NS2)              ──┤
 │    ├── AGVType (NS2)                ──┤
 │    └── WarehouseType (NS2)          ──┤
 │                                      └─→ RobotType
 ├── ProductionOrderType (NS2)
 │    ├── PartAType (NS2)
 │    └── PartBType (NS2)
 └── ScheduleTaskType (NS2)
```

### 2.3 CNC 信息模型（完整 NodeId）

**CNCMachineType (ns=2;s=CNCMachineType)**

```
CNC-001 (ns=2;s=CNC-001, type=CNCMachineType)
├── Identification (ns=2;s=CNC-001.Identification)
│   ├── SerialNumber    (ns=2;s=CNC-001.Identification.SerialNumber)    String  "CMX600-2024-001"
│   ├── Manufacturer    (ns=2;s=CNC-001.Identification.Manufacturer)    String  "DMG Mori"
│   ├── Model           (ns=2;s=CNC-001.Identification.Model)           String  "CMX 600 V"
│   └── FirmwareVersion (ns=2;s=CNC-001.Identification.FirmwareVersion) String  "3.2.1"
│
├── Status (ns=2;s=CNC-001.Status)
│   ├── MachineState    (ns=2;s=CNC-001.Status.MachineState)    Int32   {0:IDLE,1:RUN,2:PAUSE,3:ALARM,4:MAINT}
│   ├── OperatingMode   (ns=2;s=CNC-001.Status.OperatingMode)   Int32   {0:AUTO,1:MDI,2:JOG,3:ZERO}
│   ├── EmergencyStop   (ns=2;s=CNC-001.Status.EmergencyStop)   Boolean
│   └── AlarmCode       (ns=2;s=CNC-001.Status.AlarmCode)       UInt16[]  [1001,2003]
│
├── Process (ns=2;s=CNC-001.Process)
│   ├── ProgramName     (ns=2;s=CNC-001.Process.ProgramName)    String  "PART-A_OP1.nc"
│   ├── ProgramLine     (ns=2;s=CNC-001.Process.ProgramLine)    UInt32
│   ├── SpindleSpeed    (ns=2;s=CNC-001.Process.SpindleSpeed)   UInt32  rpm
│   ├── SpindleLoad     (ns=2;s=CNC-001.Process.SpindleLoad)    Double  %
│   ├── FeedRate        (ns=2;s=CNC-001.Process.FeedRate)       UInt32  mm/min
│   ├── FeedOverride    (ns=2;s=CNC-001.Process.FeedOverride)   Double  % (0-200)
│   └── CycleTime       (ns=2;s=CNC-001.Process.CycleTime)      Double  seconds
│
├── Tooling (ns=2;s=CNC-001.Tooling)
│   ├── ActiveTool      (ns=2;s=CNC-001.Tooling.ActiveTool)     UInt16  T-code
│   ├── ToolLife        (ns=2;s=CNC-001.Tooling.ToolLife)       Double[30]  min remaining
│   └── ToolOffset      (ns=2;s=CNC-001.Tooling.ToolOffset)     Double[30]  mm
│
├── Sensors (ns=2;s=CNC-001.Sensors)
│   ├── VibrationX      (ns=2;s=CNC-001.Sensors.VibrationX)     Double  mm/s²
│   ├── VibrationY      (ns=2;s=CNC-001.Sensors.VibrationY)     Double  mm/s²
│   ├── VibrationZ      (ns=2;s=CNC-001.Sensors.VibrationZ)     Double  mm/s²
│   ├── Temperature     (ns=2;s=CNC-001.Sensors.Temperature)    Double  °C
│   ├── PowerConsumed   (ns=2;s=CNC-001.Sensors.PowerConsumed)  Double  kW
│   └── CoolantFlow     (ns=2;s=CNC-001.Sensors.CoolantFlow)    Double  L/min
│
├── Production (ns=2;s=CNC-001.Production)
│   ├── CurrentOrder    (ns=2;s=CNC-001.Production.CurrentOrder)    String  OrderID
│   ├── PartCount       (ns=2;s=CNC-001.Production.PartCount)       UInt32  today
│   ├── RejectCount     (ns=2;s=CNC-001.Production.RejectCount)     UInt32  today
│   └── OEE             (ns=2;s=CNC-001.Production.OEE)             Double  % (A×P×Q)
│
├── Methods (ns=2;s=CNC-001.Methods)
│   ├── Start            输入:(ProgramName, PartType) → 输出:(JobID, StatusCode)
│   ├── Stop              输入:() → 输出:(StatusCode)
│   ├── Pause             输入:() → 输出:(StatusCode)
│   ├── Resume            输入:() → 输出:(StatusCode)
│   ├── ResetAlarm        输入:(AlarmCode) → 输出:(StatusCode)
│   ├── LoadProgram       输入:(ProgramID) → 输出:(StatusCode)
│   └── SetOverride       输入:(Axis, Value%) → 输出:(StatusCode)
│
└── Alarms (ns=2;s=CNC-001.Alarms)  [HasEventSource → ns=2;s=CNC-001.AlarmEvents]
    ├── ActiveAlarms    (ns=2;s=CNC-001.Alarms.ActiveAlarms)    UInt16[]
    └── AlarmHistory    (ns=2;s=CNC-001.Alarms.AlarmHistory)    UInt16[100]
```

### 2.4 机器人信息模型

```
ROB-001 (ns=2;s=ROB-001, type=RobotType)
├── Identification     同CNC结构 (省略)
├── Status
│   ├── RobotState      Int32   {0:IDLE,1:MOVE,2:GRIP,3:WELD,4:ALARM,5:TEACH}
│   ├── EStop           Boolean
│   └── SpeedOverride   Double   0-100%
├── Motion
│   ├── JointAngles     Double[6]  degrees {J1..J6}
│   ├── JointTorques    Double[6]  Nm
│   ├── JointTemps      Double[6]  °C
│   ├── TCP_X/Y/Z       Double[3]  mm (Tool Center Point)
│   ├── TCP_RX/RY/RZ    Double[3]  degrees
│   └── TCP_Speed       Double     mm/s
├── Gripper
│   ├── GripState       Boolean    0=Open, 1=Closed
│   ├── GripForce       Double     N
│   └── GripWidth       Double     mm
├── Production          同CNC结构
└── Methods
    ├── MoveTo          输入:(X,Y,Z,RX,RY,RZ,Speed) → 输出:(StatusCode)
    ├── MoveJoint       输入:(J1..J6,Speed) → 输出:(StatusCode)
    ├── Grip             输入:(Force) → 输出:(StatusCode)
    ├── Release          输入:() → 输出:(StatusCode)
    └── Home             输入:() → 输出:(StatusCode)
```

### 2.5 AGV 信息模型

```
AGV-001 (ns=2;s=AGV-001, type=AGVType)
├── Status
│   ├── AGVState        Int32   {0:IDLE,1:MOVE,2:LOAD,3:UNLOAD,4:CHARGE,5:ALARM}
│   ├── BatteryLevel    Double   % (0-100)
│   └── BatteryVoltage  Double   V
├── Navigation
│   ├── PositionX       Double   mm
│   ├── PositionY       Double   mm
│   ├── Orientation     Double   degrees
│   ├── Speed           Double   mm/s
│   ├── CurrentSegment  String   "SEG-0001"
│   └── Destination     String   "WH_A01"
├── Cargo
│   ├── HasLoad         Boolean
│   ├── LoadType        String   "PART-A"/"PART-B"/"RAW"/"EMPTY"
│   └── LoadWeight      Double   kg
└── Methods
    ├── GoTo            输入:(DestID) → 输出:(StatusCode)
    ├── Dock             输入:(DockID) → 输出:(StatusCode)
    ├── Charge           输入:() → 输出:(StatusCode)
    └── EStop            输入:() → 输出:(StatusCode)
```

### 2.6 仓库信息模型

```
WH-001 (ns=2;s=WH-001, type=WarehouseType)
├── Status
│   ├── WHState         Int32   {0:NORMAL,1:FULL,2:MAINT,3:ALARM}
│   └── OccupancyRate   Double   %
├── Stacker (堆垛机)
│   ├── PositionX/Y/Z   Double[3]
│   ├── Speed           Double   m/s
│   └── TaskState       Int32
├── Inventory (库存)
│   ├── TotalSlots      UInt32   200
│   ├── OccupiedSlots   UInt32
│   ├── PartA_Stock     UInt32
│   ├── PartB_Stock     UInt32
│   ├── RawStock_A      UInt32   kg
│   └── RawStock_B      UInt32   kg
└── Methods
    ├── StoreRequest    输入:(SlotID,MaterialType) → 输出:(StatusCode)
    ├── RetrieveRequest  输入:(SlotID,MaterialType) → 输出:(StatusCode)
    └── InventoryScan    输入:() → 输出:(InventoryReport)
```

### 2.7 数据影子模型 (四个影子路径)

每个 Variable 节点按时间序列记录四态值：

| 路径 | 含义 | 示例 | 触发场景 |
|------|------|------|----------|
| `/happy` | 正常数据 | SpindleSpeed=8000 | 设备正常运行中 |
| `/nil` | nil/null | SpindleSpeed=nil | 传感器未初始化、设备断电 |
| `/empty` | 空值但非nil | SpindleSpeed=0 | 设备空转但未发生加工 |
| `/error` | 错误/异常 | SpindleSpeed=-1 | 传感器故障、通信中断 |

```
时间序列存储结构:
CNC-001/Process/SpindleSpeed
├── [T1] {happy: 8000, nil: false, empty: false, error: false}
├── [T2] {happy: 0,    nil: false, empty: true,  error: false}
├── [T3] {happy: nil,  nil: true,  empty: false, error: false}
└── [T4] {happy: nil,  nil: false, empty: false, error: "SENSOR_FAULT_0x1A"}
```

---

## 第三章：Python 数字孪生类定义

### 3.1 核心类图

```
                    ┌─────────────────────┐
                    │    DigitalTwinBase   │ (抽象基类)
                    │  +device_id: str     │
                    │  +state: Enum        │
                    │  +shadow: DataShadow │
                    │  +sync_from_physical │
                    │  +sync_to_physical   │
                    │  +simulate()         │
                    └─────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────┴────┐          ┌─────┴─────┐         ┌────┴─────┐
   │ CNCTwin │          │ RobotTwin │         │  AGVTwin │
   └─────────┘          └───────────┘         └──────────┘
```

### 3.2 基础类定义

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
import json

# ═══════════════════════════════════════════════
# 数据影子模型
# ═══════════════════════════════════════════════

class ShadowState(IntEnum):
    HAPPY = 0
    NIL = 1
    EMPTY = 2
    ERROR = 3

@dataclass
class DataPoint:
    """每个传感器读数的四态记录"""
    timestamp: datetime
    value: Any
    shadow: ShadowState
    error_code: Optional[str] = None

    @classmethod
    def happy(cls, value: Any) -> 'DataPoint':
        return cls(datetime.now(), value, ShadowState.HAPPY)

    @classmethod
    def nil(cls) -> 'DataPoint':
        return cls(datetime.now(), None, ShadowState.NIL)

    @classmethod
    def empty(cls) -> 'DataPoint':
        return cls(datetime.now(), None, ShadowState.EMPTY)

    @classmethod
    def error(cls, code: str) -> 'DataPoint':
        return cls(datetime.now(), None, ShadowState.ERROR, code)

@dataclass
class DataShadow:
    """管理一个设备的所有影子数据"""
    device_id: str
    history: Dict[str, List[DataPoint]] = field(default_factory=dict)
    max_history: int = 1000

    def record(self, key: str, dp: DataPoint):
        if key not in self.history:
            self.history[key] = []
        self.history[key].append(dp)
        if len(self.history[key]) > self.max_history:
            self.history[key] = self.history[key][-self.max_history:]

    def latest(self, key: str) -> Optional[DataPoint]:
        seq = self.history.get(key, [])
        return seq[-1] if seq else None

    def latest_happy(self, key: str) -> Optional[Any]:
        for dp in reversed(self.history.get(key, [])):
            if dp.shadow == ShadowState.HAPPY:
                return dp.value
        return None

# ═══════════════════════════════════════════════
# 状态枚举
# ═══════════════════════════════════════════════

class CNCState(IntEnum):
    IDLE = 0; RUN = 1; PAUSE = 2; ALARM = 3; MAINT = 4

class RobotState(IntEnum):
    IDLE = 0; MOVE = 1; GRIP = 2; WELD = 3; ALARM = 4; TEACH = 5

class AGVState(IntEnum):
    IDLE = 0; MOVE = 1; LOAD = 2; UNLOAD = 3; CHARGE = 4; ALARM = 5

class WarehouseState(IntEnum):
    NORMAL = 0; FULL = 1; MAINT = 2; ALARM = 3

# ═══════════════════════════════════════════════
# 异常定义
# ═══════════════════════════════════════════════

class DigitalTwinError(Exception): pass
class SyncError(DigitalTwinError): pass
class SimulationError(DigitalTwinError): pass
class CommunicationError(DigitalTwinError): pass

# ═══════════════════════════════════════════════
# 抽象基类
# ═══════════════════════════════════════════════

class DigitalTwinBase(ABC):
    """数字孪生抽象基类。定义了物理实体同步、模拟运行、状态管理的通用接口。"""

    def __init__(self, device_id: str, opcua_node_id: str):
        self.device_id = device_id
        self.opcua_node_id = opcua_node_id
        self.shadow = DataShadow(device_id)
        self._state: IntEnum = self._initial_state()
        self._last_sync: Optional[datetime] = None
        self._error: Optional[str] = None

    # ---------- 子类必须实现 ----------

    @abstractmethod
    def _initial_state(self) -> IntEnum: ...

    @abstractmethod
    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        """验证从物理设备读取的原始数据是否在合理范围内"""
        ...

    @abstractmethod
    def simulate(self, delta_t: float) -> Dict[str, Any]:
        """不连接物理设备时运行一步仿真，返回仿真传感器数据"""
        ...

    # ---------- 通用实现 ----------

    def sync_from_physical(self, raw_data: Dict[str, Any]) -> bool:
        """从物理设备同步数据到数字孪生。返回 True 表示同步成功。"""
        self._last_sync = datetime.now()
        self._error = None

        if not self._validate_hardware_state(raw_data):
            self._error = f"HARDWARE_VALIDATION_FAILED for {self.device_id}"
            self.shadow.record("sync_status", DataPoint.error(self._error))
            return False

        for key, value in raw_data.items():
            dp: DataPoint
            if value is None:
                dp = DataPoint.nil()
            elif isinstance(value, (list, dict, str)) and len(value) == 0:
                dp = DataPoint.empty()
            elif isinstance(value, (int, float)) and value < -900:
                dp = DataPoint.error(f"SENSOR_OUT_OF_RANGE:{key}")
            else:
                dp = DataPoint.happy(value)
            self.shadow.record(key, dp)

        self._on_sync_success(raw_data)
        self.shadow.record("sync_status", DataPoint.happy(True))
        return True

    def _on_sync_success(self, raw_data: Dict[str, Any]):
        """同步成功后的回调，子类可覆盖以更新派生状态"""
        pass

    def get_state(self) -> IntEnum:
        return self._state

    def health_report(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "state": self._state.name,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "error": self._error,
            "shadow_keys": list(self.shadow.history.keys()),
        }
```

### 3.3 CNC 数字孪生

```python
import math

@dataclass
class CNCConfig:
    max_spindle_speed: int = 12000
    max_feed_rate: int = 20000    # mm/min
    tool_count: int = 30
    max_power: float = 22.0       # kW
    normal_temp_range: tuple = (15.0, 65.0)  # °C
    vibration_warn: float = 7.0   # mm/s²
    vibration_critical: float = 12.0

class CNCTwin(DigitalTwinBase):
    """CNC 数控机床数字孪生。维护机床状态、刀具寿命、工艺参数。"""

    def __init__(self, device_id: str, opcua_node_id: str, config: Optional[CNCConfig] = None):
        super().__init__(device_id, opcua_node_id)
        self.config = config or CNCConfig()
        self.tool_life: List[float] = [100.0] * self.config.tool_count
        self.current_program: Optional[str] = None
        self.part_count_today: int = 0
        self.reject_count_today: int = 0

    def _initial_state(self) -> CNCState:
        return CNCState.IDLE

    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        spindle = raw.get("spindle_speed")
        if spindle is not None and (spindle < 0 or spindle > self.config.max_spindle_speed * 1.1):
            return False

        temp = raw.get("temperature")
        if temp is not None and (temp > 85.0 or temp < -10.0):
            return False  # 超出物理可行范围

        vibration = raw.get("vibration_x")
        if vibration is not None and vibration > self.config.vibration_critical * 2:
            return False  # 传感器故障

        return True

    def _on_sync_success(self, raw_data: Dict[str, Any]):
        super()._on_sync_success(raw_data)
        # 更新刀具寿命
        active_tool = raw_data.get("active_tool")
        cycle_time = raw_data.get("cycle_time")
        if active_tool is not None and cycle_time is not None:
            idx = active_tool - 1
            if 0 <= idx < len(self.tool_life):
                self.tool_life[idx] -= cycle_time / 60.0  # 分钟消耗

        new_state = raw_data.get("machine_state")
        if new_state is not None:
            self._state = CNCState(new_state)

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        """模拟 CNC 加工一步。delta_t: 秒"""
        if self._state == CNCState.RUN:
            # 模拟主轴运转
            target_rpm = 8000
            actual_rpm = target_rpm + math.sin(datetime.now().timestamp()) * 50
            actual_rpm = max(0, min(actual_rpm, self.config.max_spindle_speed))

            # 模拟振动
            base_vib = 2.5
            noise = (hash(str(datetime.now().timestamp())) % 100) / 100 * 1.5
            tool_wear_factor = (100 - min(self.tool_life)) / 100 * 3.0

            return {
                "spindle_speed": round(actual_rpm),
                "spindle_load": round(35 + noise * 10, 1),
                "feed_rate": 500,
                "temperature": round(38 + noise * 5 + tool_wear_factor * 5, 1),
                "vibration_x": round(base_vib + noise + tool_wear_factor, 2),
                "vibration_y": round(base_vib + noise * 0.8 + tool_wear_factor * 0.9, 2),
                "vibration_z": round(base_vib * 0.7 + noise * 0.6, 2),
                "power_consumed": round(12 + noise * 3, 1),
                "coolant_flow": 15.0,
                "cycle_time": delta_t,
                "machine_state": self._state.value,
            }
        else:
            return {
                "spindle_speed": 0, "spindle_load": 0, "feed_rate": 0,
                "temperature": 25.0, "vibration_x": 0.0, "vibration_y": 0.0,
                "vibration_z": 0.0, "power_consumed": 0.5, "coolant_flow": 0.0,
                "cycle_time": 0, "machine_state": self._state.value,
            }

    def start_program(self, program: str, part_type: str) -> str:
        if self._state == CNCState.ALARM:
            raise SimulationError(f"Cannot start: {self.device_id} in ALARM state")
        self.current_program = program
        self._state = CNCState.RUN
        return f"JOB-{self.device_id}-{datetime.now():%Y%m%d%H%M%S}"

    def emergency_stop(self):
        self._state = CNCState.ALARM
        self.shadow.record("emergency_stop", DataPoint.happy(datetime.now().isoformat()))

    def tool_change_needed(self) -> List[int]:
        """返回需要更换的刀具编号列表(寿命 < 10%)"""
        return [i + 1 for i, life in enumerate(self.tool_life) if life < 10.0]
```

### 3.4 机器人数字孪生

```python
import numpy as np

class RobotTwin(DigitalTwinBase):
    """六轴机器人数字孪生。维护关节状态、TCP位姿、夹爪状态。"""

    JOINT_LIMITS = [
        (-180, 180), (-130, 130), (-230, 65),
        (-190, 190), (-120, 120), (-360, 360)
    ]

    def __init__(self, device_id: str, opcua_node_id: str):
        super().__init__(device_id, opcua_node_id)
        self.joint_angles: List[float] = [0.0] * 6
        self.tcp_position: List[float] = [0.0, 0.0, 0.0]  # X,Y,Z mm
        self.tcp_orientation: List[float] = [0.0, 0.0, 0.0]  # RX,RY,RZ deg
        self.grip_state: bool = False  # False=开, True=闭
        self.speed_override: float = 100.0

    def _initial_state(self) -> RobotState:
        return RobotState.IDLE

    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        angles = raw.get("joint_angles")
        if angles and len(angles) == 6:
            for i, (a, (lo, hi)) in enumerate(zip(angles, self.JOINT_LIMITS)):
                if a < lo - 5 or a > hi + 5:  # 5°容差
                    return False
        return True

    def _on_sync_success(self, raw_data: Dict[str, Any]):
        super()._on_sync_success(raw_data)
        if "joint_angles" in raw_data:
            self.joint_angles = raw_data["joint_angles"]
        if "tcp_x" in raw_data:
            self.tcp_position = [
                raw_data.get("tcp_x", 0),
                raw_data.get("tcp_y", 0),
                raw_data.get("tcp_z", 0),
            ]

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        if self._state == RobotState.MOVE:
            jitter = [(hash(str(datetime.now().timestamp() + i)) % 100) / 100 * 0.1
                       for i in range(6)]
            angles = [a + j for a, j in zip(self.joint_angles, jitter)]
        else:
            angles = self.joint_angles

        torques = [abs(ang) * 0.5 + 2.0 + (hash(str(datetime.now().timestamp() + i + 10)) % 100) / 200
                   for i, ang in enumerate(angles)]

        return {
            "robot_state": self._state.value,
            "joint_angles": [round(a, 4) for a in angles],
            "joint_torques": [round(t, 2) for t in torques],
            "joint_temps": [round(35 + t * 0.5, 1) for t in torques],
            "tcp_x": round(self.tcp_position[0], 3),
            "tcp_y": round(self.tcp_position[1], 3),
            "tcp_z": round(self.tcp_position[2], 3),
            "tcp_rx": self.tcp_orientation[0],
            "tcp_ry": self.tcp_orientation[1],
            "tcp_rz": self.tcp_orientation[2],
            "tcp_speed": 200.0 if self._state == RobotState.MOVE else 0.0,
            "grip_state": self.grip_state,
            "grip_force": 50.0 if self.grip_state else 0.0,
        }

    def move_to(self, x, y, z, rx, ry, rz, speed=200.0):
        self.tcp_position = [x, y, z]
        self.tcp_orientation = [rx, ry, rz]
        self.speed_override = speed
        self._state = RobotState.MOVE

    def grip(self, force: float = 50.0):
        self.grip_state = True
        self._state = RobotState.GRIP

    def release(self):
        self.grip_state = False
        self._state = RobotState.IDLE
```

### 3.5 AGV 数字孪生

```python
class AGVTwin(DigitalTwinBase):
    """AGV 数字孪生。维护位置、电池、载货状态。"""

    def __init__(self, device_id: str, opcua_node_id: str):
        super().__init__(device_id, opcua_node_id)
        self.position: List[float] = [0.0, 0.0]
        self.battery: float = 100.0
        self.has_load: bool = False
        self.destination: Optional[str] = None

    def _initial_state(self) -> AGVState: return AGVState.IDLE

    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        battery = raw.get("battery_level")
        if battery is not None and (battery < -1 or battery > 102):
            return False
        return True

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        if self._state == AGVState.MOVE:
            speed = 1000.0  # mm/s
            dist = speed * delta_t / 1000.0
            self.battery -= delta_t * 0.002  # 每秒耗电 0.2%
            self.battery = max(0, self.battery)

        return {
            "agv_state": self._state.value,
            "position_x": round(self.position[0], 1),
            "position_y": round(self.position[1], 1),
            "battery_level": round(self.battery, 2),
            "has_load": self.has_load,
            "destination": self.destination or "",
        }

    def go_to(self, dest: str):
        self.destination = dest
        self._state = AGVState.MOVE

    def needs_charge(self) -> bool:
        return self.battery < 20.0
```

### 3.6 数字孪生管理器

```python
class DigitalTwinManager:
    """管理所有数字孪生实例，提供统一的同步和查询接口。"""

    def __init__(self):
        self._twins: Dict[str, DigitalTwinBase] = {}

    def register(self, twin: DigitalTwinBase):
        self._twins[twin.device_id] = twin

    def get(self, device_id: str) -> Optional[DigitalTwinBase]:
        return self._twins.get(device_id)

    def sync_all(self, data_source: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """从数据源批量同步所有设备。data_source: {device_id: {key: value}}"""
        results = {}
        for device_id, raw_data in data_source.items():
            twin = self._twins.get(device_id)
            if twin:
                results[device_id] = twin.sync_from_physical(raw_data)
            else:
                results[device_id] = False
        return results

    def simulate_all(self, delta_t: float) -> Dict[str, Dict[str, Any]]:
        return {dev_id: twin.simulate(delta_t)
                for dev_id, twin in self._twins.items()}

    def all_health_reports(self) -> Dict[str, Dict[str, Any]]:
        return {dev_id: twin.health_report()
                for dev_id, twin in self._twins.items()}

    def get_idle_cncs(self) -> List[str]:
        return [dev_id for dev_id, t in self._twins.items()
                if isinstance(t, CNCTwin) and t.get_state() == CNCState.IDLE]

    def get_available_robots(self) -> List[str]:
        return [dev_id for dev_id, t in self._twins.items()
                if isinstance(t, RobotTwin) and t.get_state() in (RobotState.IDLE, RobotState.GRIP)]
```

### 3.7 OPC UA 连接器

```python
# 注意：此模块需要 opcua-asyncio 包
# pip install opcua-asyncio

class OPCUAConnector:
    """连接 OPC UA 服务器，读取设备节点数据并转换为同步格式。"""

    def __init__(self, server_url: str):
        self.server_url = server_url  # e.g., "opc.tcp://192.168.1.100:4840"
        self.subscriptions: Dict[str, List[str]] = {}  # {device_id: [node_ids]}

    # 顶层调用流程:
    # 1. connect() → client
    # 2. for each device: read_nodes(device_node_id) → raw_data
    # 3. dt_manager.sync_all(raw_data)

    async def connect(self):
        """异步连接 OPC UA 服务器 (框架代码)"""
        # from asyncua import Client
        # client = Client(url=self.server_url)
        # await client.connect()
        # return client
        raise NotImplementedError("需要 opcua-asyncio 运行时")

    async def read_device_nodes(self, client, device_id: str,
                                 node_mapping: Dict[str, str]) -> Dict[str, Any]:
        """读取设备的所有监控节点。
        node_mapping: {逻辑名称: OPC UA NodeId 字符串}
        """
        results = {}
        for logical_name, node_id_str in node_mapping.items():
            try:
                # var = client.get_node(node_id_str)
                # value = await var.read_value()
                # results[logical_name] = value
                pass
            except Exception:
                results[logical_name] = None  # → DataPoint.nil()
        return results
```

---

## 第四章：实时数据流架构

### 4.1 数据流总览

```
Level 4 (ERP)               SAP S/4HANA
                                │
                    生产计划 (BAPI)
                                │
                                ▼
Level 3 (MES)    ┌──────────────────────────────┐
                 │        MES System             │
                 │  ┌────────┐  ┌──────────┐     │
                 │  │订单管理│  │工艺管理  │     │
                 │  └────┬───┘  └────┬─────┘     │
                 │       └─────┬─────┘           │
                 │       ┌─────┴─────┐           │
                 │       │调度引擎    │           │
                 │       │(RL Scheduler)│         │
                 │       └─────┬─────┘           │
                 │       ┌─────┴─────┐           │
                 │       │OPC UA Client│          │
                 │       └─────┬─────┘           │
                 └─────────────┼────────────────┘
                               │
                     OPC UA TCP (opc.tcp://:4840)
                               │
Level 2 (SCADA)  ┌─────────────┼────────────────┐
                 │    ┌────────┴────────┐        │
                 │    │ OPC UA Server   │        │
                 │    │  (地址空间)     │        │
                 │    └────────┬────────┘        │
                 │    ┌────────┴────────┐        │
                 │    │ 数据缓冲区/TSDB │        │
                 │    │  (InfluxDB)     │        │
                 │    └────────┬────────┘        │
                 └─────────────┼────────────────┘
                               │
Level 1 (PLC)    ┌─────────────┼────────────────┐
                 │   PLC-001 ──┤── PLC-002 ...   │
                 │   (CNC Zone) │  (Robot Zone)  │
                 └─────────────┼────────────────┘
                               │
Level 0 (Field)  ┌─────────────┼────────────────┐
                 │   Sensors, Actuators, RFID    │
                 │   Profibus / EtherCAT / IO-Link│
                 └──────────────────────────────┘
```

### 4.2 数据流详细路径

```
路径A — 上行(物理→数字):
Field → PLC (IO采集, 10ms周期)
 PLC → OPC UA Server (Modbus TCP/Profinet, 100ms)
  OPC UA Server → MES OPC UA Client (Subscription, 500ms)
   MES → DigitalTwinManager.sync_all(raw_data)
    DigitalTwinManager → 各Twin.sync_from_physical()
     Twin → DataShadow.record() (四态判断)
      DataShadow → TimescaleDB/InfluxDB (持久化)

路径B — 下行(数字→物理):
 MES Scheduler → 调度决策 WorkOrder
  MES → Twin.simulate() (验证可行性)
   MES → OPC UA Client.call_method(MethodNode)
    OPC UA Server → PLC (写寄存器/调用功能块)
     PLC → Actuator (输出执行)

路径C — 事件驱动(异常→报警):
 Sensor → Value out of range
  Twin._validate_hardware_state() → False
   → DataPoint.error() 写入 Shadow
    → MES AlarmManager.publish("ALARM", device_id, error_code)
     → SCADA HMI 推送 (WebSocket/MQTT)
      → 邮件/短信/钉钉 通知
```

### 4.3 数据格式定义

**上传数据包 (Device → MES, JSON over OPC UA)**

```json
{
  "device_id": "CNC-001",
  "timestamp": "2026-05-02T10:15:30.500Z",
  "seq": 48291,
  "data": {
    "machine_state": 1,
    "spindle_speed": 7998,
    "feed_rate": 500,
    "temperature": 42.3,
    "vibration_x": 3.21
  },
  "alarms": [],
  "quality": {
    "data_valid": true,
    "sensor_health": "OK"
  }
}
```

**下行指令包 (MES → Device, JSON over OPC UA Method Call)**

```json
{
  "command_id": "CMD-20260502-001",
  "device_id": "CNC-001",
  "method": "Start",
  "params": {
    "program_name": "PART-A_OP1.nc",
    "part_type": "PART-A"
  },
  "priority": "NORMAL",
  "timeout_ms": 5000
}
```

---

## 第五章：MES-PLC 交互序列

### 5.1 标准加工流程 (快乐路径)

```
时间线    MES                      OPC UA Server           PLC / Device
──────    ───                      ─────────────           ────────────
T=0      生成生产订单 WO-001
         查询可用设备: CNC-001 IDLE
         │
T=1      Call Start(CNC-001,         ──────────────────→  收到Start请求
          "PART-A_OP1.nc")                                加载G代码程序
         │                                                主轴预热3s
         │                                                冷却液开启
         │                                                → RUNNING
         │                          ←──────────────────   MachineState=1
T=2      收到 State=RUNNING
         Record: 开始计时
         │
T=3..N   Subscription 500ms         ←→                   实时推送传感器数据
         持续监控振动/温度/负载                             加工执行中...
         │
T=N+1                              ←──────────────────   加工完成
         │                                                → IDLE
         │                          ←──────────────────   MachineState=0
T=N+2    收到 State=IDLE
         检查 PartCount 增量
         生成 QC Inspection Task
         WO-001 → COMPLETED
```

### 5.2 异常暂停与恢复流程

```
时间线    MES                      OPC UA Server           PLC / Device
──────    ───                      ─────────────           ────────────
T=0      CNC-001 RUNNING                                  加工中
T=1                                                    【刀具破损检测】
         │                          ←──────────────────   AlarmCode=2003
         │                          ←──────────────────   MachineState=3(ALARM)
T=2      收到 AlarmCode=2003 (TOOL_BREAK)
         │
         ├→ Publish Alarm to SCADA HMI
         ├→ 通知操作员 (钉钉/短信)
         ├→ 查询替代设备 CNC-003 IDLE?
         ├→ 如启用: 自动切换至 CNC-003
         └→ 创建 Maintenance Task MT-001
         │
T=5      操作员确认换刀完成
         │
         Call ResetAlarm(CNC-001)  ──────────────────→  清除报警
         │                          ←──────────────────   MachineState=0(IDLE)
         │
         Call Start(CNC-001,                               重新加工
           "PART-A_OP1.nc")        ──────────────────→
```

### 5.3 机器人上下料序列

```
ROB-001 上料流程
═══════════════

Step 1: MES → AGV-001: GoTo("CNC-001_UNLOAD")
         AGV-001 → MES: State=3(UNLOAD), Position=DOCK
Step 2: MES → ROB-001: MoveTo(CNC_chuck_x, y, z, rx, ry, rz)
         ROB-001 → MES: State=1(MOVE)
Step 3: MES → ROB-001: Grip(force=50N)
         ROB-001 → MES: GripState=true, State=GRIP
Step 4: ROB-001 取出成品 → 放置于AGV托盘
Step 5: MES → ROB-001: Release()
         ROB-001 → MES: GripState=false, State=IDLE
Step 6: MES → ROB-001: MoveTo(raw_material_xyz)
         ROB-001 → MES: State=1(MOVE)
Step 7: MES → ROB-001: Grip(force=50N)
Step 8: ROB-001 取毛坯 → 放置于CNC卡盘
Step 9: MES → ROB-001: Release()
Step 10: MES → CNC-001: Start("PART-A_OP1.nc", "PART-A")

总耗时目标: ≤ 45 秒
```

### 5.4 AGV 物料运输序列

```
AGV-001 任务: 将成品从CNC区运至仓库
══════════════════════════════════

Phase 1 — 调度
  MES Scheduler: AGV-001 IDLE → 分配任务 "TRANSPORT-042"
  目标: CNC-ZONE-UNLOAD → WH-ZONE-INBOUND

Phase 2 — 出发
  MES → AGV-001: GoTo("CNC-ZONE-UNLOAD")
  AGV-001: 规划路径 (A*算法, 避开ROB工作区)
  沿途 RFID 定位桩: TAG-001 → TAG-007 → TAG-012

Phase 3 — 装载
  AGV-001 → MES: 到达, State=LOAD
  ROB-001 完成放置 → AGV-001.HasLoad=true

Phase 4 — 运输
  MES → AGV-001: GoTo("WH-ZONE-INBOUND")
  Path: TAG-012 → TAG-020 → TAG-035 → TAG-050

Phase 5 — 卸载
  AGV-001 → MES: 到达, State=UNLOAD
  WH-001 Stacker → 接收货物
  AGV-001 → MES: HasLoad=false, State=IDLE

Phase 6 — 充电检查
  if AGV-001.battery < 20%:
      MES → AGV-001: GoTo("CHARGE-STATION-01")
      AGV-001 → MES: State=CHARGE
```

---

## 第六章：强化学习动态调度

### 6.1 马尔可夫决策过程定义

**调度问题被建模为 MDP：**

```
MDP = (S, A, P, R, γ)

S — 状态空间:
  For each device:
    - state: {IDLE, RUN, ALARM, etc.}
    - queue_length: 等待任务数
    - remaining_time: 当前任务剩余时间
    - tool_life_min: 最小刀具寿命
    - oee: 设备综合效率
  Global:
    - part_a_demand: 剩余 A 零件需求
    - part_b_demand: 剩余 B 零件需求
    - current_time: 当前班次时间
    - energy_total: 累计能耗

A — 动作空间:
  For each idle_device × available_task:
    - assign(device_id, task_id)
  Plus:
    - WAIT (不分配,等待)
    - REROUTE (重新路由到备用设备)

R — 奖励函数 (见6.2)

γ — 折扣因子: 0.99
```

### 6.2 奖励函数设计

```python
def reward_function(prev_state: dict, action: str, new_state: dict) -> float:
    """
    奖励函数由四个加权项组成。
    设计原则：完工时间最小化 + 质量最优 + 能耗意识 + 设备保护
    """

    # 1. 产出奖励 — 完成任务
    throughput = 0.0
    if task_completed(new_state):
        # PART-A: +10, PART-B: +8 (反映利润差异)
        throughput = 10.0 if task_type == "PART-A" else 8.0

    # 2. 设备利用率平衡 — 避免某个设备过载
    utilizations = [dev["utilization"] for dev in new_state["devices"]]
    balance_penalty = -abs(max(utilizations) - min(utilizations)) * 0.5

    # 3. 能耗惩罚 — 鼓励在低电价时段排产
    energy = new_state.get("energy_kwh", 0) - prev_state.get("energy_kwh", 0)
    energy_cost = -energy * electricity_price(new_state["current_time"])

    # 4. 设备健康惩罚 — 保护高磨损设备
    health = 0.0
    for dev in new_state["devices"]:
        if dev["tool_life_min"] < 15:  # 刀具寿命 < 15min
            health -= 2.0  # 惩罚使用即将需要换刀的机床

    # 5. 延迟惩罚 — 每延误1分钟扣分
    lateness_penalty = 0.0
    for task in overdue_tasks(new_state):
        lateness_penalty -= max(0, task["delay_minutes"]) * 0.1

    return throughput + balance_penalty + energy_cost + health + lateness_penalty

def electricity_price(hour: int) -> float:
    """分时电价 (元/kWh)"""
    if 8 <= hour < 11: return 1.2   # 峰
    if 11 <= hour < 14: return 1.5   # 尖峰
    if 14 <= hour < 19: return 1.2   # 峰
    if 19 <= hour < 22: return 0.8   # 平
    return 0.4  # 谷
```

### 6.3 Double DQN 训练算法 (完整伪代码)

```
Algorithm: Double DQN for Smart Manufacturing Scheduling

Hyperparameters:
  η = 0.0005           (学习率)
  γ = 0.99              (折扣因子)
  ε_start = 1.0          (初始探索率)
  ε_end = 0.01           (最终探索率)
  ε_decay = 2000         (衰减步数)
  M = 10000              (经验回放池容量)
  B = 64                 (批量大小)
  C = 100                (目标网络更新频率: 每100步)
  T = 50000              (总训练步数)

初始化:
  Q_main ← 随机初始化权重 (网络: 128→256→256→|A|)
  Q_target ← Q_main (同结构,参数冻结)
  经验池 D ← deque(maxlen=M)
  step = 0

for episode in 1..E:
    s = 初始状态 (从仿真环境获取)
    total_reward = 0

    while not done:   # done: 所有订单完成或超时
        # ε-贪心动作选择
        ε = ε_end + (ε_start - ε_end) * exp(-step / ε_decay)
        if random() < ε:
            a = random_action(s)    # 随机调度
        else:
            a = argmax Q_main(s, a) # 贪心调度

        # 执行动作
        s', r, done = env.step(a)   # env = ManufacturingEnv (仿真器)
        total_reward += r

        # 存入经验回放
        D.append((s, a, r, s', done))
        step += 1

        # 采样训练
        if len(D) >= B:
            batch = random_sample(D, B)
            train_step(batch)

        # 更新目标网络
        if step % C == 0:
            Q_target ← Q_main

        s = s'

def train_step(batch):
    for each (s, a, r, s', done) in batch:

        # Double DQN: 用 main 选动作,用 target 评估
        if done:
            target = r
        else:
            a* = argmax Q_main(s', a')      # 主网络选最优动作
            target = r + γ * Q_target(s', a*)  # 目标网络评估

        # 梯度下降
        loss = (Q_main(s, a) - target)²
        optimizer.step(loss)

Network Architecture:
  Input: 状态向量 (dim=42)  → 状态编码
  Hidden: FC(128) + ReLU + Dropout(0.1)
          FC(256) + ReLU + Dropout(0.1)
          FC(256) + ReLU
  Output: Q值向量 (dim=8)   → 每个可能的动作
```

### 6.4 状态编码器

```python
import torch
import torch.nn as nn

class ManufacturingStateEncoder(nn.Module):
    """将车间状态编码为固定维度的特征向量"""

    def __init__(self, n_devices=7, n_tasks_max=20):
        super().__init__()
        # 设备特征: 状态(one-hot 5) + 利用率 + 队列长度 + 刀具寿命 + OEE = 9维
        # 全局特征: A需求 + B需求 + 当前时间 + 累计能耗 = 4维
        # 总输入: 7*9 + 4 = 67维
        self.fc1 = nn.Linear(67, 128)
        self.fc2 = nn.Linear(128, 256)
        self.fc3 = nn.Linear(256, 256)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(torch.relu(self.fc2(x)))
        x = torch.relu(self.fc3(x))
        return x  # 256-dim state embedding
```

### 6.5 调度仿真器

```python
class ManufacturingEnv:
    """制造车间调度仿真环境。用于 RL 训练。"""

    def __init__(self, dt_manager: DigitalTwinManager):
        self.dt = dt_manager
        self.current_time = 0.0  # 仿真时钟, 秒
        self.order_queue: List[Dict] = []
        self.completed_orders: List[Dict] = []

    def reset(self) -> np.ndarray:
        self.current_time = 0.0
        self.order_queue = self._generate_orders()
        self.completed_orders.clear()
        return self._encode_state()

    def step(self, action: int) -> tuple:
        """
        执行一个调度动作，返回 (next_state, reward, done, info)
        action: 0=分配CNC-001, 1=CNC-002, 2=CNC-003,
                3=ROB-001, 4=ROB-002, 5=AGV-001,
                6=WAIT, 7=REROUTE
        """
        prev_state = self._get_metrics()
        self._execute_action(action)
        self.current_time += 30  # 仿真30秒步长
        self._advance_simulation(30)

        next_state = self._get_metrics()
        reward = reward_function(prev_state, action, next_state)
        done = len(self.completed_orders) >= len(self.order_queue)
        return self._encode_state(), reward, done, {"completed": len(self.completed_orders)}

    def _execute_action(self, action: int):
        """将动作映射到实际设备调度"""
        device_map = {0: "CNC-001", 1: "CNC-002", 2: "CNC-003",
                       3: "ROB-001", 4: "ROB-002", 5: "AGV-001"}
        if action in device_map:
            device = device_map[action]
            if self._is_device_idle(device) and self.order_queue:
                task = self.order_queue.pop(0)
                self._assign_task(device, task)

    def _encode_state(self) -> np.ndarray:
        """编码当前状态为 67 维向量"""
        vec = []
        for dev_id in ["CNC-001", "CNC-002", "CNC-003",
                        "ROB-001", "ROB-002", "AGV-001", "WH-001"]:
            twin = self.dt.get(dev_id)
            state_onehot = [0]*5
            state_onehot[twin.get_state().value % 5] = 1 if twin else 0
            util = len(getattr(twin, 'current_program', '')) > 0
            vec.extend(state_onehot + [float(util), 0.0, 0.0, 0.8])

        # 全局特征
        demand_a = sum(1 for o in self.order_queue if o.get("type") == "PART-A")
        demand_b = sum(1 for o in self.order_queue if o.get("type") == "PART-B")
        vec.extend([demand_a, demand_b,
                     self.current_time / 86400,  # 归一化到天
                     0.0])
        return np.array(vec, dtype=np.float32)
```

---

## 第七章：故障场景分析

### 7.1 场景矩阵

| # | 设备 | 故障 | 严重度 | 发生概率 | 检测延迟 |
|---|------|------|--------|---------|---------|
| FA-01 | CNC-001 | 刀具破损 | 中 | 0.5次/班 | <1s |
| FA-02 | CNC-002 | 主轴轴承过热 | 高 | 0.02次/班 | 30s |
| FA-03 | CNC-003 | 冷却液不足 | 低 | 0.1次/班 | 5s |
| FA-04 | ROB-001 | J3关节过载 | 高 | 0.01次/班 | <0.1s |
| FA-05 | ROB-002 | 夹爪丢失工件 | 中 | 0.05次/班 | 2s |
| FA-06 | AGV-001 | 电池低电量 | 低 | 1次/天 | <1s |
| FA-07 | AGV-001 | 路径阻塞 | 中 | 0.2次/班 | 3s |
| FA-08 | WH-001 | 堆垛机定位错 | 高 | 0.01次/班 | 5s |
| FA-09 | Network | OPC UA 断连 | 高 | 0.02次/天 | 15s |
| FA-10 | Sensor | 振动传感器零漂 | 低 | 0.1次/天 | 需要分析 |

### 7.2 详细故障分析 (FA-01: CNC刀具破损)

```
┌─────────────────────────────────────────────────────────────┐
│ FA-01: CNC-001 加工中刀具破损                                │
├─────────────────────────────────────────────────────────────┤
│ 触发条件:                                                    │
│   - 主轴负载 > 85% 持续 2 秒                                 │
│   - 振动 X/Y 轴 > 警报阈值 (7.0 mm/s²)                       │
│   - 刀具寿命 < 5% 且未及时更换                                │
│                                                             │
│ 影响链:                                                      │
│   CNC-001 → ALARM (AlarmCode=2003)                          │
│   → 当前工件作废 (RejectCount+1)                              │
│   → 后续工序物料短缺                                          │
│   → 如替代设备不可用 → 积压 WIP                               │
│                                                             │
│ 检测手段:                                                    │
│   T+0.5s: 主轴负载阈值触发                                    │
│   T+1.0s: 振动传感器超限确认                                  │
│   T+1.0s: OPC UA AlarmEvent 推送                             │
│   T+1.5s: MES AlarmManager 收到事件                           │
│                                                             │
│ 恢复步骤:                                                    │
│   1. CNC-001 自动退刀 + 主轴停转 (PLC 逻辑)                   │
│   2. MES 发布报警到 SCADA + 通知值班员                        │
│   3. MES 评估: CNC-003 是否可用? 是 → 转移任务               │
│   4. 创建维修工单: 换刀 + 对刀 + 首件检验                     │
│   5. 操作员确认 → ResetAlarm → 试切合格 → 恢复生产            │
│   6. 更新刀具寿命计数器                                       │
│                                                             │
│ 恢复时间目标: 15 min (含换刀 10min + 首件验证 5min)           │
│                                                             │
│ 预防措施:                                                    │
│   - 刀具寿命 < 15% 时 MES 提前提醒换刀                        │
│   - 振动趋势分析 (升高 → 预警)                                │
│   - 刀具批次溯源 (如有连续3把同批次破损 → 停用该批次)           │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 FA-09: OPC UA 通信中断

```
┌─────────────────────────────────────────────────────────────┐
│ FA-09: MES ↔ OPC UA Server 通信中断                          │
├─────────────────────────────────────────────────────────────┤
│ 触发条件:                                                    │
│   - 网络链路断开 (交换机故障 / 网线拔除 / 光纤断)             │
│   - OPC UA Server 进程崩溃                                   │
│   - TLS 证书过期                                             │
│   - 防火墙规则变更                                            │
│                                                             │
│ 影响链:                                                      │
│   MES 失去实时数据 → 数字孪生进入"盲飞"状态                    │
│   → 调度引擎使用最后一次已知状态 (保守策略)                    │
│   → 无法下发新指令 → 设备继续执行当前任务直至完成              │
│   → 如持续 > 60s → 触发安全停机通知                           │
│                                                             │
│ 检测手段:                                                    │
│   T+0s:    最后一次成功 Subscription 回调                    │
│   T+15s:   心跳超时 (KeepAlive interval = 5s, 3×超时)        │
│   T+15s:   MES ConnectionManager 标记: DISCONNECTED          │
│   T+16s:   SCADA HMI 显示 "OPC UA Offline"                   │
│                                                             │
│ 恢复步骤:                                                    │
│   1. MES 尝试重连 (指数退避: 1s → 2s → 4s → 8s ... max 60s) │
│   2. 重连成功 → 调用 Republish 获取丢失期间的数据              │
│   3. DigitalTwinManager.sync_all() 批量同步                   │
│   4. 检查数据一致性: 对比 PartCount 增量 vs 仿真预测            │
│   5. 如有偏差 → 人工确认 → 手动修正                            │
│   6. 恢复正常订阅                                             │
│                                                             │
│ 恢复时间目标: < 30s (网络故障) / < 5min (服务器重启)          │
│                                                             │
│ 预防措施:                                                    │
│   - OPC UA Server 冗余部署 (主备, 虚拟IP)                     │
│   - 设备端 PLC 自带数据缓冲 (断网 5min 内数据不丢失)           │
│   - 每月检查 TLS 证书到期日期                                 │
└─────────────────────────────────────────────────────────────┘
```

### 7.4 剩余场景速览

**FA-02 — 主轴轴承过热:**
触发: Temperature > 65°C ⟹ CNC → ALARM, 自动降速 50% (如温升趋势 > 2°C/min)
影响: 精度下降 (热膨胀), 如继续运行 → 轴承抱死
恢复: 冷却 20min → 热补偿参数重标定 → 首件检验 → 恢复

**FA-05 — 夹爪丢失工件:**
触发: GripForce < 5N 持续 0.5s (工件滑落) 或 GripWidth 异常
影响: 工件坠落 → 可能损伤导轨 + 节拍打断
恢复: ROB → IDLE, 人工检查工作区, 确认无损伤后 Reset → 重新抓取

**FA-07 — AGV 路径阻塞:**
触发: 激光雷达检测障碍物 (0-3m 范围内, 持续时间 > 2s)
影响: 运输延迟 → 下游设备待料
恢复: 等待 5s → 重新规划路径 → 如仍阻塞 → 报警通知清除障碍 → 手动接管

**FA-10 — 振动传感器零漂:**
触发: 振动值 = 0.0mm/s² 持续 10s (设备运行中不可能为绝对零)
影响: 刀具破损检测失效, 预防性维护预警失效
恢复: 标记传感器异常 → 使用主轴负载信号作为备用检测 → 计划停机更换传感器

---

## 第八章：架构决策记录 (ADR)

### ADR-1: 选择 OPC UA 而非 MQTT + Sparkplug B

**状态:** ACCEPTED  
**日期:** 2026-05-02  
**决策者:** 系统架构师  
**业务需求:** BR-001 (设备互联互通), BR-005 (安全合规)

**背景:**
工业设备互联有两种主流方案：OPC UA (IEC 62541) 和 MQTT + Sparkplug B。需要确定设备层建模和通信的标准。

**方案对比:**

| 维度 | OPC UA | MQTT + Sparkplug B |
|------|--------|---------------------|
| 信息建模 | 原生支持,类型系统完善 | Sparkplug B 定义有限 |
| 安全 | 内置 3 级安全策略 + 证书 | 依赖 TLS,无内建安全模型 |
| 方法调用 | 原生 Method Node | 需要自定义 RPC 机制 |
| 实时性 | Subscription+Publish,ms级 | Pub/Sub,依赖 Broker |
| 互操作性 | 1000+ Companion Specs | 主要面向 SCADA 集成 |
| 学习曲线 | 陡峭 | 平缓 |

**决策:**
选择 OPC UA 作为设备层通信和建模的标准。

**理由:**
1. 信息建模能力是核心需求——每个设备需要复杂的类型定义（CNCType 有 40+ 节点），MQTT 的扁平 Topic 无法胜任
2. 安全合规——OPC UA 内置 Sign & Encrypt、用户认证、审计日志，满足 IEC 62443 要求
3. Method Node 使工厂能直接调用设备功能（Start/Stop/ResetAlarm），无需额外的 RPC 层
4. 可扩展——未来新增设备类型只需扩展类型定义，客户端代码无需修改

**后果:**
- 需要 OPC UA 专业知识 (学习曲线)
- 需要部署 OPC UA Server (额外的中间件)
- OPC UA 二进制协议调试较 TCP/JSON 困难

---

### ADR-2: 数字孪生层使用 Python 异步架构

**状态:** ACCEPTED  
**日期:** 2026-05-02  
**决策者:** 系统架构师  
**业务需求:** BR-002 (实时性 < 500ms), BR-004 (可仿真测试)

**背景:**
数字孪生需要同时维护 7 个设备的状态、处理实时数据流、运行仿真。需要在 Python 同步、Python 异步、Go、C++ 之间选择。

**决策:**
使用 Python asyncio + opcua-asyncio 作为数字孪生运行时。

**理由:**
1. Python 是数据科学和 ML 生态的首选语言——RL 调度模块 (PyTorch) 和数据分析 (NumPy/Pandas) 天然适配
2. asyncio 足够满足 500ms 实时性要求（OPC UA Subscription 本身 100-500ms 周期）
3. 仿真模式可以脱离物理硬件运行——方便开发和 CI 测试
4. Go/C++ 虽然性能更好，但团队需要维护两套 ML 管道（训练用 Python，推理用另一语言）

**后果:**
- 如果未来扩展到 100+ 设备，可能需要 Go 重写高性能采集层
- GIL 限制：CPU 密集型数值计算需要移植到 NumPy/Cython
- 需要 OPC UA async 库的成熟度验证

---

### ADR-3: 调度采用 Double DQN 而非规则引擎或 OR-Tools

**状态:** ACCEPTED  
**日期:** 2026-05-02  
**决策者:** 系统架构师  
**业务需求:** BR-003 (动态调度), BR-006 (持续优化)

**背景:**
车间调度方案有三种技术路线：启发式规则引擎、运筹学 (OR-Tools / CPLEX)、强化学习。

**决策:**
采用 Double DQN 作为核心调度算法，规则引擎作为冷启动和降级策略。

**理由:**
1. 车间状态是高维且动态变化的——规则引擎无法覆盖所有情况（仅规则就需要 50+ 条）
2. OR-Tools 需要每轮重新求解，求解时间不可预测 (NP-hard, 可能 30s+)
3. Double DQN 训练后推理 < 1ms，可实时在线调度
4. RL 可通过仿真器持续训练优化，无需人工调参

**后果:**
- 训练需要大量仿真数据 (50000+ episodes)
- 冷启动阶段使用规则引擎 (先到先服务 + 最短加工时间优先)
- 策略可解释性低——需要可视化 Q 值热力图辅助理解

---

### ADR-4: 采用 Purdue 模型 + OPC UA DMZ 的安全架构

**状态:** ACCEPTED  
**日期:** 2026-05-02  
**决策者:** 安全架构师  
**业务需求:** BR-005 (安全合规), BR-007 (远程监控)

**背景:**
工业控制系统面临 IT/OT 融合带来的安全挑战。需要在功能开放性和安全隔离之间取得平衡。

**决策:**
严格按照 ISA-99/IEC 62443 Purdue 模型分层，在 Level 3-4 之间部署 DMZ。

**理由:**
1. 油田、电力、制药行业的主流做法，合规性有保障
2. OPC UA 反向代理在 DMZ 终止外部连接，车间网络不可达
3. 纵深防御：即使 DMZ 被突破，PLC 层仍受独立防火墙保护

**后果:**
- 增加了网络拓扑的复杂度和硬件成本
- DMZ 数据同步有延迟 (镜像数据库 +100ms)
- 运维需要同时管理 IT 和 OT 两套网络策略

---

### ADR-5: SQL + TimescaleDB 混合存储而非纯时序数据库

**状态:** ACCEPTED  
**日期:** 2026-05-02  
**决策者:** 系统架构师  
**业务需求:** BR-008 (数据追溯), BR-009 (报表查询)

**背景:**
车间数据包括两种类型：结构化业务数据（订单、工单、库存）和高频时序数据（传感器、振动、温度）。

**决策:**
PostgreSQL + TimescaleDB 扩展处理时序数据，保持业务数据和时序数据在同一数据库。

**理由:**
1. 减少运维复杂度——一套数据库而不是两套
2. JOIN 查询可以直接跨订单表和传感器表,无需 ETL
3. TimescaleDB 的自动分区和压缩能处理 7 设备 × 40 变量 × 2Hz = 560 点/秒

**后果:**
- 500Hz+ 高频振动数据需要在应用层做降采样
- 纯 InfluxDB 的写入吞吐量更高，但 SQL 生态不如 PG 成熟

---

### ADR-6: 数据影子四态模型

**状态:** ACCEPTED  
**日期:** 2026-05-02  
**决策者:** 系统架构师  
**业务需求:** BR-010 (数据质量), BR-011 (故障诊断)

**背景:**
传感器数据存在多种异常状态：断连 (nil)、静止但通电 (empty/zero)、故障 (error)。需要统一的分类方法。

**决策:**
为每个数据点维护四态影子 (Happy / Nil / Empty / Error)，在 sync_from_physical 时自动分类。

**理由:**
1. 区分 nil 和 empty 对故障诊断至关重要——"传感器未响应"和"设备停机中"触发不同的响应
2. 数据分析时可以只取 happy 路径做高质量训练集
3. 错误分类在录入端完成，下游消费者无需重复判断

**后果:**
- 存储量翻倍 (每个值需要额外 2 bytes 标记)
- 需要在传感器协议转换器中处理边界情况

---

### ADR-7: JSON over OPC UA 而非 OPC UA Binary

**状态:** ACCEPTED  
**日期:** 2026-05-02  
**决策者:** 系统架构师  
**业务需求:** BR-012 (可调试性), BR-001 (互操作性)

**背景:**
OPC UA 支持两种数据编码：UA Binary (高效) 和 UA JSON (可读)。

**决策:**
MES 与 OPC UA Server 之间使用 UA Binary 传输，应用层负载使用 JSON。

**理由:**
1. OPC UA 二进制协议由 SDK 自动处理编码/解码
2. 应用层 JSON 方便日志查看、Wireshark 抓包调试、集成测试断言
3. 纯 Binary 方案调试时间成本过高

**后果:**
- 有效载荷比纯 Binary 大约 1.5-2x
- 需要确保 JSON 编码不引入精度丢失 (浮点数使用字符串传输或限制小数位)

---

### ADR-8: 统一生产/仿真架构 (vs 分离式 vs 全物理引擎)

**状态:** ACCEPTED  
**日期:** 2026-05-02  
**决策者:** 系统架构师  
**业务需求:** BR-002 (实时性), BR-003 (动态调度), BR-004 (可仿真测试)

**背景:**
代码与仿真有三种架构关系：分离式（生产代码和仿真代码各自独立）、统一式（仿真器是数字孪生的特化模式）、全仿真驱动式（数字孪生本质是仿真引擎+标定层）。需要选择一种作为系统基础架构。

**决策:**
采用统一式架构：仿真器是 DigitalTwinManager 的薄包装。同一个孪生对象同时服务生产和训练。生产模式走 `sync_from_physical()`，仿真模式走 `simulate()`，两者输出完全相同的 state vector 形状。

**理由:**
1. RL 策略在训练期间看到的状态空间与部署期间完全一致——消除了 sim-to-real gap 中最棘手的形状不匹配问题
2. 生产模式和仿真模式共享同一套状态编码器 (`_encode_state()`)，代码量减少 ~30%
3. 故障恢复时的"仿真预测 vs 实际数据"一致性检查变得 trivial——同一个对象两个模式
4. 不需要维护两套状态机逻辑（分离式方案中 CNCTwin 和 ManufacturingEnv 各自实现状态转换）

**核心设计约束:**
- `sync_from_physical(raw_data)` 和 `simulate(delta_t)` 必须返回相同结构的 `Dict[str, Any]`
- `DigitalTwinManager._encode_state()` 是唯一的 state → vector 路径
- `ManufacturingEnv` 退化为对 `DigitalTwinManager` 的 RL 适配层（step/reset/reward）

**后果:**
- `simulate()` 需要覆盖所有 `sync_from_physical()` 可能产生的 key
- 仿真精度依赖 `simulate()` 中物理简化模型的保真度
- 需要额外的标定步骤：用真实数据拟合 `simulate()` 的噪声参数

---

## 第十一章：统一生产/仿真架构详细设计

### 11.1 核心原则

**一个对象，两种模式：**

```
                    ┌──────────────────────┐
                    │   DigitalTwinManager  │
                    │                      │
                    │  mode: "production"   │──── sync_all(opcua_data)
                    │  mode: "simulation"   │──── simulate_all(delta_t)
                    │                      │
                    │  _encode_state()  ◄──│──── 唯一的状态向量化路径
                    │  _decode_action() ◄──│──── 唯一的动作解码路径
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
         CNCTwin          RobotTwin         AGVTwin
              │                │                │
    sync_from_physical()  sync_from_physical()  sync_from_physical()
    simulate()            simulate()            simulate()
              │                │                │
              └────────────────┼────────────────┘
                               │
                    相同的输出结构
                    {key: value, ...}
```

**关键不变式：**
1. 无论是 `sync_from_physical()` 还是 `simulate()`，返回的 dict key 集合必须相同
2. `_encode_state()` 不接受任何模式参数——它对两种模式完全透明
3. RL 策略在仿真中训练，直接部署到生产中，无需任何适配层

### 11.2 统一的 Twin 接口

在每个 Twin 类中，`sync_from_physical()` 和 `simulate()` 输出相同的 key 集合：

```python
# CNC Twin 必须保证两种模式输出相同的 key
CNC_OUTPUT_KEYS = [
    "machine_state",    # IntEnum → int
    "spindle_speed",    # UInt32
    "spindle_load",     # Double
    "feed_rate",        # UInt32
    "temperature",      # Double
    "vibration_x",      # Double
    "vibration_y",      # Double
    "vibration_z",      # Double
    "power_consumed",   # Double
    "coolant_flow",     # Double
    "cycle_time",       # Double
]
```

### 11.3 统一的 ManufacturingEnv (重构后)

```python
class ManufacturingEnv:
    """RL 仿真环境 —— DigitalTwinManager 的薄包装。

    设计原则：
    - 不重复任何状态逻辑——全部委托给 DigitalTwinManager
    - step() = 动作解码 → 孪生仿真推进 → 状态编码 → 奖励计算
    - 同一套代码既可用于 RL 训练（simulate 模式），
      也可用于生产验证（sync 模式），只需切换 manager 的数据源
    """

    def __init__(self, dt_manager: DigitalTwinManager):
        self.dt = dt_manager
        self.current_time: float = 0.0
        self.order_queue: List[Order] = []
        self.completed: List[Order] = []
        self._step_count: int = 0

    def reset(self, orders: Optional[List[Order]] = None) -> np.ndarray:
        """重置环境。可选地注入生产订单列表。"""
        self.current_time = 0.0
        self._step_count = 0
        self.order_queue = orders or self._generate_default_orders()
        self.completed.clear()
        # 将所有孪生重置为初始状态
        for twin in self.dt._twins.values():
            twin._state = twin._initial_state()
        return self._encode_state()  # ← 唯一的编码路径

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        """执行一步调度动作。

        Args:
            action: 0=assign CNC-001, 1=CNC-002, 2=CNC-003,
                    3=ROB-001, 4=ROB-002, 5=AGV-001, 6=WAIT, 7=REROUTE
        Returns:
            (next_state, reward, done, info)
        """
        prev_metrics = self._get_metrics()

        # 1. 动作解码 + 执行（委托给 manager 中的孪生对象）
        self._execute_action(action)

        # 2. 时间推进 + 物理仿真
        delta_t = 30.0  # 30秒步长
        self.current_time += delta_t

        # 关键：simulate_all() 和 sync_all() 产生相同结构的数据
        sim_data = self.dt.simulate_all(delta_t)
        # 如果是在生产模式下验证，将 sim_data 替换为 sync_data:
        # sim_data = self._latest_opcua_snapshot

        # 3. 更新孪生内部状态（从仿真数据）
        for dev_id, data in sim_data.items():
            twin = self.dt.get(dev_id)
            if twin:
                twin._on_sync_success(data)  # 复用同一回调

        # 4. 状态编码 + 奖励
        next_metrics = self._get_metrics()
        reward = self._compute_reward(prev_metrics, action, next_metrics)

        done = len(self.completed) >= len(self.order_queue) or self._step_count > 1000
        self._step_count += 1

        return (
            self._encode_state(),  # ← 唯一的编码路径
            reward,
            done,
            {"completed": len(self.completed), "step": self._step_count},
        )

    def _encode_state(self) -> np.ndarray:
        """唯一的状态编码路径。
        生产模式和仿真模式在这里完全统一 ——
        编码器不关心数据来自 sync 还是 simulate。
        """
        vec = []
        # 设备特征：7 设备 × 9 维 = 63 维
        for dev_id in ["CNC-001", "CNC-002", "CNC-003",
                        "ROB-001", "ROB-002", "AGV-001", "WH-001"]:
            twin = self.dt.get(dev_id)
            state_val = twin.get_state().value if twin else 0
            state_onehot = [0] * 6  # 最多 6 种状态
            state_onehot[min(state_val, 5)] = 1

            # 利用率 = 是否有正在执行的任务
            has_active = 0
            if isinstance(twin, CNCTwin):
                has_active = 1 if twin.current_program else 0
            elif isinstance(twin, RobotTwin):
                has_active = 1 if twin.get_state() == RobotState.MOVE else 0
            elif isinstance(twin, AGVTwin):
                has_active = 1 if twin.destination else 0

            # 队列长度、刀具寿命、设备效率（从 shadow 取最新 happy 值）
            queue_len = len([o for o in self.order_queue
                             if self._task_fits_device(o, dev_id)])
            tool_life_min = min(twin.tool_life) if isinstance(twin, CNCTwin) and twin.tool_life else 100.0

            vec.extend(state_onehot + [
                float(has_active),      # 利用率标志
                float(queue_len) / 10,  # 归一化队列长度
                tool_life_min / 100,    # 归一化刀具寿命
            ])  # 6 + 3 = 9 维

        # 全局特征：4 维
        demand_a = sum(1 for o in self.order_queue if o.part_type == "PART-A")
        demand_b = sum(1 for o in self.order_queue if o.part_type == "PART-B")
        vec.extend([
            demand_a / 50.0,             # 归一化
            demand_b / 50.0,
            self.current_time / 86400,   # 归一化到天
            self._compute_total_energy() / 500.0,
        ])

        return np.array(vec, dtype=np.float32)

    def _execute_action(self, action: int):
        """将动作映射到孪生对象的方法调用"""
        device_map = {0: "CNC-001", 1: "CNC-002", 2: "CNC-003",
                       3: "ROB-001", 4: "ROB-002", 5: "AGV-001"}

        if action in device_map and self.order_queue:
            dev_id = device_map[action]
            twin = self.dt.get(dev_id)
            if twin and self._is_idle(twin):
                order = self._find_best_task(dev_id)
                if order:
                    self._assign_to_twin(twin, order)

    def _assign_to_twin(self, twin: DigitalTwinBase, order: Order):
        """统一的设备任务分配——生产模式和仿真模式共用"""
        if isinstance(twin, CNCTwin):
            twin.start_program(order.program, order.part_type)
        elif isinstance(twin, RobotTwin):
            twin.move_to(*order.target_pose, speed=200)
        elif isinstance(twin, AGVTwin):
            twin.go_to(order.destination)
        order.assigned_device = twin.device_id
        order.started_at = self.current_time

    def _compute_reward(self, prev: dict, action: int, next: dict) -> float:
        """奖励函数——使用与生产环境完全相同的计算逻辑"""
        r = 0.0
        # 产出奖励
        for order in self.order_queue:
            if order.completed and not order._rewarded:
                r += 10.0 if order.part_type == "PART-A" else 8.0
                order._rewarded = True
        # 平衡惩罚
        utils = [next.get(f"{dev}_util", 0) for dev in ["CNC-001", "CNC-002", "CNC-003"]]
        r -= abs(max(utils) - min(utils)) * 0.5
        # 能耗
        delta_energy = next.get("total_energy", 0) - prev.get("total_energy", 0)
        r -= delta_energy * 0.8  # 平均电价
        # 延迟惩罚
        for order in self.order_queue:
            if order.due_time and self.current_time > order.due_time:
                r -= (self.current_time - order.due_time) / 60 * 0.1
        return r

    def _get_metrics(self) -> dict:
        """获取当前全局指标——生产和仿真通用"""
        devices = {}
        for dev_id, twin in self.dt._twins.items():
            shadow = twin.shadow
            spindle = shadow.latest_happy("spindle_speed")
            devices[f"{dev_id}_util"] = 1.0 if (spindle and spindle > 0) else 0.0
        return {
            **devices,
            "total_energy": self._compute_total_energy(),
            "time": self.current_time,
            "queue_depth": len(self.order_queue),
            "completed": len(self.completed),
        }

    def _compute_total_energy(self) -> float:
        total = 0.0
        for dev_id, twin in self.dt._twins.items():
            power = twin.shadow.latest_happy("power_consumed")
            if power and power > 0:
                total += power * self.current_time / 3600  # kWh
        return total

    def _is_idle(self, twin: DigitalTwinBase) -> bool:
        state = twin.get_state()
        if isinstance(twin, CNCTwin):
            return state == CNCState.IDLE
        if isinstance(twin, RobotTwin):
            return state in (RobotState.IDLE,)
        if isinstance(twin, AGVTwin):
            return state == AGVState.IDLE
        return False

    def _find_best_task(self, dev_id: str) -> Optional[Order]:
        """为设备找最优待处理任务（SPT 启发式作为 fallback）"""
        candidates = [o for o in self.order_queue
                      if not o.assigned and self._task_fits_device(o, dev_id)]
        if not candidates:
            return None
        # 最短加工时间优先（RL 动作可覆盖此默认选择）
        return min(candidates, key=lambda o: o.estimated_duration)

    def _task_fits_device(self, order: Order, dev_id: str) -> bool:
        if dev_id.startswith("CNC"):
            return order.part_type in ("PART-A", "PART-B")
        if dev_id.startswith("ROB"):
            return order.operation in ("LOAD", "UNLOAD")
        if dev_id.startswith("AGV"):
            return order.operation == "TRANSPORT"
        return False

@dataclass
class Order:
    """生产订单——生产和仿真共用"""
    order_id: str
    part_type: str           # "PART-A" | "PART-B"
    operation: str           # "OP10" | "OP20" | "TRANSPORT" | "LOAD" | "UNLOAD"
    program: str             # G代码文件名
    target_pose: Optional[Tuple[float, ...]] = None  # 机器人目标位姿
    destination: Optional[str] = None  # AGV 目标点
    estimated_duration: float = 240.0  # 预估加工时间(秒)
    due_time: Optional[float] = None
    assigned_device: Optional[str] = None
    started_at: Optional[float] = None
    completed: bool = False
    _rewarded: bool = False  # 防止重复给奖励
```

### 11.4 生产/仿真模式切换

```python
class DigitalTwinManager:
    """扩展后的管理器，支持模式切换"""

    def __init__(self):
        self._twins: Dict[str, DigitalTwinBase] = {}
        self.mode: str = "simulation"  # "simulation" | "production"
        self._opcua_connector: Optional[OPCUAConnector] = None

    def set_mode(self, mode: str):
        if mode not in ("simulation", "production"):
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode

    def step_all(self, delta_t: float) -> Dict[str, Dict[str, Any]]:
        """统一的推进接口——根据模式选择数据源"""
        if self.mode == "production":
            # 从 OPC UA 读取真实数据
            if not self._opcua_connector:
                raise DigitalTwinError("OPC UA connector not initialized in production mode")
            return self.sync_all(self._opcua_connector.fetch_all())
        else:
            # 使用仿真数据
            return self.simulate_all(delta_t)

    def verify_consistency(self, sim_data: dict, real_data: dict) -> List[str]:
        """检查仿真数据与真实数据的一致性，返回差异列表"""
        discrepancies = []
        for dev_id in sim_data:
            if dev_id in real_data:
                for key in sim_data[dev_id]:
                    sim_val = sim_data[dev_id].get(key)
                    real_val = real_data[dev_id].get(key)
                    if sim_val is not None and real_val is not None:
                        if isinstance(sim_val, (int, float)) and isinstance(real_val, (int, float)):
                            if abs(sim_val - real_val) > abs(real_val) * 0.2:  # 20% 容差
                                discrepancies.append(
                                    f"{dev_id}.{key}: sim={sim_val:.2f}, real={real_val:.2f}"
                                )
        return discrepancies
```

### 11.6 物理仿真模型

ADR-8-bis 决策：`simulate()` 使用基于常微分方程的物理模型，而非统计噪声。

#### 11.6.1 CNC 主轴动力学模型

```python
class CNCTwin(DigitalTwinBase):
    """CNC 数字孪生 — 使用 ODE 物理模型进行仿真"""

    # ═══ 物理参数 (标称值, 从 DMG Mori CMX 600 手册获取) ═══

    SPINDLE_INERTIA = 0.12       # J: kg·m² (主轴 + 刀柄 + 刀具转动惯量)
    SPINDLE_DAMPING = 0.008      # b: Nm/(rad/s) (轴承粘性阻尼)
    MOTOR_TORQUE_MAX = 35.0      # τ_max: Nm (主轴电机峰值扭矩)
    CUTTING_FORCE_COEFF = 0.15   # K_c: Nm/(rpm) (切削力→扭矩系数, 材料相关)

    THERMAL_CAPACITY = 8500.0    # C: J/K (主轴箱 + 电机热容)
    THERMAL_RESISTANCE = 0.025   # R: K/W (主轴箱→环境的等效热阻)
    AMBIENT_TEMP = 22.0          # T_amb: °C
    MOTOR_EFFICIENCY = 0.88      # η: 电机效率 (功率损耗→热)

    VIBRATION_MASS = 2.5         # m: kg (主轴箱等效质量)
    VIBRATION_STIFFNESS = 2.4e6  # k: N/m (轴承等效刚度)
    VIBRATION_DAMPING = 1200.0   # c: N·s/m (结构阻尼)

    TOOL_WEAR_RATE = 0.02        # 刀具磨损率 μm/s (40Cr 合金钢)
    TOOL_CRITICAL_WEAR = 150.0   # 临界磨损 μm

    def __init__(self, device_id: str, opcua_node_id: str, config=None):
        super().__init__(device_id, opcua_node_id)
        # 动态状态变量
        self._omega: float = 0.0         # 主轴角速度 (rad/s)
        self._temperature: float = self.AMBIENT_TEMP
        self._tool_wear: float = 0.0     # 当前刀具磨损 (μm)
        self._vib_x: float = 0.0         # 振动位移 (mm)
        self._vib_vx: float = 0.0        # 振动速度 (mm/s)
        self.tool_life: List[float] = [100.0] * 30

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        """一步物理仿真 —— 求解主轴 + 热 + 振动的耦合 ODE"""

        dt = min(delta_t, 0.01)  # 仿真子步长 10ms
        n_steps = int(delta_t / dt)

        target_omega = self._target_speed_rpm() * 2 * math.pi / 60

        for _ in range(n_steps):
            # ── 主轴动力学: dω/dt = (τ_motor - τ_cut - b·ω) / J ──
            tau_motor = self._motor_torque(target_omega, self._omega)
            tau_cut = self._cutting_torque() if self._state == CNCState.RUN else 0.0
            tau_friction = self.SPINDLE_DAMPING * self._omega

            domega_dt = (tau_motor - tau_cut - tau_friction) / self.SPINDLE_INERTIA
            self._omega += domega_dt * dt
            self._omega = max(0, min(self._omega, target_omega * 1.05))

            # ── 热力学: C·dT/dt = Q_gen - (T - T_amb)/R ──
            if self._state == CNCState.RUN:
                q_gen = tau_motor * self._omega * (1 - self.MOTOR_EFFICIENCY)
            else:
                q_gen = 0.0
            q_dissipate = (self._temperature - self.AMBIENT_TEMP) / self.THERMAL_RESISTANCE
            dT_dt = (q_gen - q_dissipate) / self.THERMAL_CAPACITY
            self._temperature += dT_dt * dt

            # ── 振动: m·ẍ + c·ẋ + k·x = F_cut(t) ──
            if self._state == CNCState.RUN:
                f_cut = tau_cut * 50  # 切削力 (N), 转换系数
            else:
                f_cut = 0.0
            acc = (f_cut - self.VIBRATION_DAMPING * self._vib_vx
                   - self.VIBRATION_STIFFNESS * self._vib_x) / self.VIBRATION_MASS
            self._vib_vx += acc * dt
            self._vib_x += self._vib_vx * dt

            # ── 刀具磨损 ──
            if self._state == CNCState.RUN and tau_cut > 0:
                wear_rate = self.TOOL_WEAR_RATE * (tau_cut / self.MOTOR_TORQUE_MAX)
                self._tool_wear += wear_rate * dt

        # 更新刀具寿命
        active_tool_idx = 0
        if self.tool_life and active_tool_idx < len(self.tool_life):
            self.tool_life[active_tool_idx] = max(
                0, 100 * (1 - self._tool_wear / self.TOOL_CRITICAL_WEAR)
            )

        return self._build_output()

    def _motor_torque(self, target_omega: float, current_omega: float) -> float:
        """简化的电机扭矩模型: P 控制 + 扭矩限制"""
        error = target_omega - current_omega
        torque = error * 0.5  # P 增益
        return max(-self.MOTOR_TORQUE_MAX, min(self.MOTOR_TORQUE_MAX, torque))

    def _cutting_torque(self) -> float:
        """切削扭矩 = 切削力系数 × 转速 (简化)"""
        if self.current_program is None:
            return 0.0
        rpm = self._omega * 60 / (2 * math.pi)
        return self.CUTTING_FORCE_COEFF * rpm * (1 + self._tool_wear / self.TOOL_CRITICAL_WEAR)

    def _target_speed_rpm(self) -> float:
        """从仿真场景获取目标转速"""
        if self._state == CNCState.RUN:
            return 8000.0  # 默认, 可被外部设置覆盖
        return 0.0

    def _build_output(self) -> Dict[str, Any]:
        """构建与 sync_from_physical() 完全相同结构的输出"""
        rpm = self._omega * 60 / (2 * math.pi)
        tau_motor = self._motor_torque(0, self._omega)  # 近似
        power = tau_motor * self._omega / 1000  # kW (如果 tau_motor < 0, 取 0)
        if power < 0:
            power = 0.0
        return {
            "machine_state": self._state.value,
            "spindle_speed": round(rpm),
            "spindle_load": round(abs(tau_motor) / self.MOTOR_TORQUE_MAX * 100, 1) if self._state == CNCState.RUN else 0,
            "feed_rate": 500 if self._state == CNCState.RUN else 0,
            "temperature": round(self._temperature, 1),
            "vibration_x": round(abs(self._vib_x) * 10, 2),   # 缩放到合理范围
            "vibration_y": round(abs(self._vib_x) * 7, 2),     # Y ≈ 0.7 × X
            "vibration_z": round(abs(self._vib_x) * 5, 2),     # Z ≈ 0.5 × X
            "power_consumed": round(power, 1),
            "coolant_flow": 15.0 if self._state == CNCState.RUN else 0.0,
            "cycle_time": 0.03,  # 仿真子步长
        }
```

#### 11.6.2 物理参数标定框架

```python
import numpy as np
from scipy.optimize import least_squares  # 或自实现梯度下降

@dataclass
class CNCPhysicsParams:
    """CNC 物理模型的可标定参数集"""
    spindle_inertia: float = 0.12
    spindle_damping: float = 0.008
    cutting_force_coeff: float = 0.15
    thermal_capacity: float = 8500.0
    thermal_resistance: float = 0.025
    vibration_stiffness: float = 2.4e6
    vibration_damping: float = 1200.0

    def to_vector(self) -> np.ndarray:
        return np.array([
            self.spindle_inertia, self.spindle_damping, self.cutting_force_coeff,
            self.thermal_capacity, self.thermal_resistance,
            self.vibration_stiffness, self.vibration_damping,
        ])

    @classmethod
    def from_vector(cls, vec: np.ndarray) -> 'CNCPhysicsParams':
        return cls(*vec)


class CalibrationEngine:
    """用真实运行数据标定仿真物理参数。

    方法: 非线性最小二乘
      min Σ (sim_output(t) - real_data(t))²
      s.t. params ∈ [0.5×nominal, 2.0×nominal]  (物理可行性约束)
    """

    def __init__(self, twin: CNCTwin):
        self.twin = twin
        self.nominal = CNCPhysicsParams()

    def calibrate(self, real_runs: List[Dict]) -> CNCPhysicsParams:
        """real_runs: [{timestamp, spindle_speed, temperature, vibration_x, ...}, ...]
        每个 run 是一段连续加工过程（启动→稳态→停止）。
        """
        def objective(param_vec):
            params = CNCPhysicsParams.from_vector(param_vec)
            self._apply_params(params)

            total_error = 0.0
            for run in real_runs:
                sim_output = self._simulate_run(run)
                # 多目标误差: 转速 + 温度 + 振动
                for key, weight in [("spindle_speed", 1.0),
                                     ("temperature", 0.5),
                                     ("vibration_x", 0.3)]:
                    if key in sim_output and key in run["data"]:
                        diff = np.mean([
                            abs(s - r) for s, r in
                            zip(sim_output[key], run["data"][key])
                        ])
                        total_error += weight * diff
            return total_error

        x0 = self.nominal.to_vector()
        bounds = (x0 * 0.5, x0 * 2.0)  # 物理可行性边界
        result = least_squares(objective, x0, bounds=bounds, max_nfev=500)
        return CNCPhysicsParams.from_vector(result.x)

    def _apply_params(self, params: CNCPhysicsParams):
        self.twin.SPINDLE_INERTIA = params.spindle_inertia
        self.twin.SPINDLE_DAMPING = params.spindle_damping
        self.twin.CUTTING_FORCE_COEFF = params.cutting_force_coeff
        self.twin.THERMAL_CAPACITY = params.thermal_capacity
        self.twin.THERMAL_RESISTANCE = params.thermal_resistance
        self.twin.VIBRATION_STIFFNESS = params.vibration_stiffness
        self.twin.VIBRATION_DAMPING = params.vibration_damping

    def _simulate_run(self, run: Dict) -> Dict[str, List[float]]:
        """重放一次加工过程，返回仿真输出序列"""
        self.twin._state = CNCState.IDLE
        self.twin._omega = 0.0
        self.twin._temperature = self.twin.AMBIENT_TEMP

        output = {"spindle_speed": [], "temperature": [], "vibration_x": []}
        dt = 0.1  # 100ms 子步

        for event in run["events"]:
            if event["type"] == "START":
                self.twin._state = CNCState.RUN
                self.twin.current_program = event.get("program")
            elif event["type"] == "STOP":
                self.twin._state = CNCState.IDLE

            sim_data = self.twin.simulate(event["duration"])
            output["spindle_speed"].append(sim_data["spindle_speed"])
            output["temperature"].append(sim_data["temperature"])
            output["vibration_x"].append(sim_data["vibration_x"])

        return output

    def check_drift(self, sim_val: float, real_val: float, key: str) -> bool:
        """在线检查仿真是否漂移"""
        if real_val == 0:
            return abs(sim_val) < 0.1
        return abs(sim_val - real_val) / abs(real_val) < 0.20  # 20% 容差
```

### 11.7 仓库数字孪生 (WarehouseTwin)

```python
from collections import deque

class WarehouseTwin(DigitalTwinBase):
    """自动化仓库数字孪生 — 简化库存模型。

    OPC UA 信息模型对应节点:
      WH-001 (ns=2;s=WH-001, type=WarehouseType)
    """

    TOTAL_SLOTS = 200  # 4排 × 10列 × 5层

    def __init__(self, device_id: str = "WH-001",
                 opcua_node_id: str = "ns=2;s=WH-001"):
        super().__init__(device_id, opcua_node_id)
        # 库存
        self.part_a_stock: int = 0
        self.part_b_stock: int = 0
        self.raw_stock_a: float = 500.0  # kg
        self.raw_stock_b: float = 300.0  # kg
        # 堆垛机
        self.stacker_pos: List[float] = [0.0, 0.0, 0.0]  # X,Y,Z (m)
        self.task_queue: deque = deque()
        self._current_task_time: float = 0.0

    def _initial_state(self) -> WarehouseState:
        return WarehouseState.NORMAL

    def _validate_hardware_state(self, raw: Dict[str, Any]) -> bool:
        stock = raw.get("part_a_stock")
        if stock is not None and (stock < 0 or stock > self.TOTAL_SLOTS):
            return False
        return True

    def _on_sync_success(self, raw_data: Dict[str, Any]):
        super()._on_sync_success(raw_data)
        if "part_a_stock" in raw_data:
            self.part_a_stock = raw_data["part_a_stock"]
        if "part_b_stock" in raw_data:
            self.part_b_stock = raw_data["part_b_stock"]
        if "raw_stock_a" in raw_data:
            self.raw_stock_a = raw_data["raw_stock_a"]
        if "raw_stock_b" in raw_data:
            self.raw_stock_b = raw_data["raw_stock_b"]

    def simulate(self, delta_t: float) -> Dict[str, Any]:
        """仓库仿真 — 消费任务队列 + 自动库存更新"""
        dt = delta_t

        # 消费堆垛机任务队列
        if self.task_queue and self._current_task_time <= 0:
            task = self.task_queue[0]
            self._current_task_time = task["duration"]
            self.stacker_pos = task.get("target_pos", self.stacker_pos)

        if self._current_task_time > 0:
            self._current_task_time -= dt
            if self._current_task_time <= 0:
                # 任务完成 — 执行库存变更
                task = self.task_queue.popleft()
                self._apply_task(task)

        # 检查库存水平
        occupancy = (self.part_a_stock + self.part_b_stock) / self.TOTAL_SLOTS
        if occupancy > 0.95:
            self._state = WarehouseState.FULL
        elif self._state == WarehouseState.FULL and occupancy < 0.85:
            self._state = WarehouseState.NORMAL

        return {
            "wh_state": self._state.value,
            "occupancy_rate": round(occupancy * 100, 1),
            "stacker_x": self.stacker_pos[0],
            "stacker_y": self.stacker_pos[1],
            "stacker_z": self.stacker_pos[2],
            "total_slots": self.TOTAL_SLOTS,
            "occupied_slots": self.part_a_stock + self.part_b_stock,
            "part_a_stock": self.part_a_stock,
            "part_b_stock": self.part_b_stock,
            "raw_stock_a": round(self.raw_stock_a, 1),
            "raw_stock_b": round(self.raw_stock_b, 1),
            "task_state": 1 if self.task_queue else 0,
        }

    def _apply_task(self, task: dict):
        """执行堆垛机任务后的库存变更"""
        op = task.get("operation")
        if op == "STORE_PART_A":
            self.part_a_stock += task.get("quantity", 1)
        elif op == "STORE_PART_B":
            self.part_b_stock += task.get("quantity", 1)
        elif op == "RETRIEVE_PART_A":
            self.part_a_stock = max(0, self.part_a_stock - task.get("quantity", 1))
        elif op == "RETRIEVE_PART_B":
            self.part_b_stock = max(0, self.part_b_stock - task.get("quantity", 1))
        elif op == "STORE_RAW_A":
            self.raw_stock_a += task.get("quantity_kg", 0)
        elif op == "CONSUME_RAW_A":
            self.raw_stock_a = max(0, self.raw_stock_a - task.get("quantity_kg", 0))
        elif op == "CONSUME_RAW_B":
            self.raw_stock_b = max(0, self.raw_stock_b - task.get("quantity_kg", 0))

    def store_request(self, material_type: str, quantity: int = 1):
        """MES 调用: 存储请求"""
        op_map = {"PART-A": "STORE_PART_A", "PART-B": "STORE_PART_B"}
        task = {
            "operation": op_map.get(material_type, "STORE_PART_A"),
            "quantity": quantity,
            "duration": 30.0,  # 30s 平均堆垛机存取时间
            "target_pos": [1.5, 2.0, 3.0],  # 示例坐标
        }
        self.task_queue.append(task)

    def retrieve_request(self, material_type: str, quantity: int = 1):
        """MES 调用: 取货请求"""
        op_map = {"PART-A": "RETRIEVE_PART_A", "PART-B": "RETRIEVE_PART_B"}
        task = {
            "operation": op_map.get(material_type, "RETRIEVE_PART_A"),
            "quantity": quantity,
            "duration": 30.0,
            "target_pos": [1.5, 2.0, 3.0],
        }
        self.task_queue.append(task)
```

### 11.8 测试策略 — 生产/仿真平行验证

统一架构的核心测试方法论：**用仿真模式跑训练好的 RL 策略，用生产模式重放历史数据，对比决策一致率。**

```
测试金字塔:

┌─────────────────────────────────────────┐
│  E2E: 48h 连续运行                       │
│  - 仿真模式 24h → 生产模式(历史回放) 24h  │
│  - 决策一致率 > 95%                       │
├─────────────────────────────────────────┤
│  集成测试:                                │
│  - 模式切换: 仿真↔生产 无状态丢失          │
│  - 数据形状: sync输出 ≈ simulate输出      │
│  - 故障注入: 通信断连 → 降级到仿真模式      │
├─────────────────────────────────────────┤
│  单元测试:                                │
│  - 每个 Twin: sync 和 simulate 输出 key 集合│
│    完全一致                               │
│  - _encode_state() 对两种数据源输出一致     │
│  - 奖励函数可单独测试 (纯数学)             │
└─────────────────────────────────────────┘
```

**关键测试用例：**

```python
def test_sync_simulate_output_shape_identical():
    """每个 Twin 的 sync_from_physical 和 simulate 必须输出相同的 key"""
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")

    sync_data = cnc.sync_from_physical({
        "spindle_speed": 8000, "temperature": 42.0, "machine_state": 1
    })
    sim_data = cnc.simulate(5.0)

    assert set(sim_data.keys()) == set(sync_data.keys()), \
        f"Key mismatch: sim={set(sim_data.keys())}, sync={set(sync_data.keys())}"


def test_encode_state_independent_of_mode():
    """状态编码不应感知数据来源"""
    manager = DigitalTwinManager()
    # ... register twins ...

    sim_vec = manager._encode_state()  # simulate 模式
    manager.set_mode("production")
    prod_vec = manager._encode_state()  # production 模式

    assert sim_vec.shape == prod_vec.shape == (67,)
    # 值可以不同（因为数据源不同），但结构和范围必须一致
    assert sim_vec.min() >= 0 and sim_vec.max() <= 1.0
    assert prod_vec.min() >= 0 and prod_vec.max() <= 1.0


def test_policy_transfer_from_sim_to_prod():
    """RL 策略从仿真部署到生产，不应需要任何适配"""
    env = ManufacturingEnv(DigitalTwinManager())
    policy = load_trained_policy("dqn_v3.pt")

    # 仿真评估
    obs = env.reset()
    sim_actions = []
    for _ in range(100):
        action = policy.select_action(obs, epsilon=0)  # 纯贪心
        obs, _, done, _ = env.step(action)
        sim_actions.append(action)
        if done: break

    # 同样的 env 切换到生产模式——不应该报错
    env.dt.set_mode("production")
    env.dt._opcua_connector = MockOPCUAConnector("replay_data/2026-05-02.csv")
    obs = env.reset()
    prod_actions = []
    for _ in range(100):
        action = policy.select_action(obs, epsilon=0)
        obs, _, done, _ = env.step(action)  # 不应该抛出任何异常
        prod_actions.append(action)
        if done: break

    # 策略在两个模式下都应产生有效动作
    assert all(0 <= a <= 7 for a in sim_actions)
    assert all(0 <= a <= 7 for a in prod_actions)
```

### 11.9 完整测试用例 (22 个缺口补充)

测试文件: `tests/unit/test_data_shadow.py`

```python
def test_shadow_record_and_retrieve():
    """DataShadow.record() 写入后 latest() 能取回"""
    shadow = DataShadow("TEST-001")
    dp = DataPoint.happy(42.0)
    shadow.record("temperature", dp)
    assert shadow.latest("temperature").value == 42.0
    assert shadow.latest("temperature").shadow == ShadowState.HAPPY

def test_shadow_empty_history_returns_none():
    """从未记录的 key，latest() 返回 None"""
    shadow = DataShadow("TEST-001")
    assert shadow.latest("nonexistent") is None

def test_shadow_history_cap():
    """历史记录超过 max_history 后截断旧数据"""
    shadow = DataShadow("TEST-001", max_history=5)
    for i in range(10):
        shadow.record("temp", DataPoint.happy(float(i)))
    assert len(shadow.history["temp"]) == 5
    assert shadow.latest("temp").value == 9.0  # 最新值保留

def test_shadow_latest_happy_skips_non_happy():
    """latest_happy() 跳过 nil/empty/error，返回最近的 happy 值"""
    shadow = DataShadow("TEST-001")
    shadow.record("speed", DataPoint.happy(100.0))
    shadow.record("speed", DataPoint.nil())
    shadow.record("speed", DataPoint.error("FAULT"))
    assert shadow.latest_happy("speed") == 100.0

def test_shadow_latest_happy_all_non_happy():
    """全部非 happy 时返回 None"""
    shadow = DataShadow("TEST-001")
    shadow.record("speed", DataPoint.nil())
    shadow.record("speed", DataPoint.error("FAULT"))
    assert shadow.latest_happy("speed") is None
```

测试文件: `tests/unit/test_sync_from_physical.py`

```python
def test_sync_happy_path():
    """正常数据全部标记为 HAPPY"""
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    result = twin.sync_from_physical({"spindle_speed": 8000, "temperature": 42.0})
    assert result is True
    assert twin.shadow.latest("spindle_speed").shadow == ShadowState.HAPPY
    assert twin.shadow.latest("spindle_speed").value == 8000

def test_sync_nil_values():
    """None 值标记为 NIL"""
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    twin.sync_from_physical({"spindle_speed": None})
    assert twin.shadow.latest("spindle_speed").shadow == ShadowState.NIL

def test_sync_empty_containers():
    """空容器标记为 EMPTY"""
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    twin.sync_from_physical({"alarms": []})
    assert twin.shadow.latest("alarms").shadow == ShadowState.EMPTY

def test_sync_out_of_range_values():
    """越界值标记为 ERROR"""
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    twin.sync_from_physical({"spindle_speed": -999})
    assert twin.shadow.latest("spindle_speed").shadow == ShadowState.ERROR
    assert "SENSOR_OUT_OF_RANGE" in twin.shadow.latest("spindle_speed").error_code

def test_sync_validation_failure():
    """硬件验证失败时返回 False 并记录错误"""
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    result = twin.sync_from_physical({"spindle_speed": 50000})  # 超出 max*1.1
    assert result is False
    assert twin.shadow.latest("sync_status").shadow == ShadowState.ERROR

def test_shadow_transition_callback():
    """shadow 状态变化时触发回调"""
    transitions = []
    twin = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    twin.on_shadow_transition = lambda key, old, new: transitions.append((key, old, new))
    twin.sync_from_physical({"spindle_speed": 8000})
    twin.sync_from_physical({"spindle_speed": None})
    assert len(transitions) == 1
    assert transitions[0] == ("spindle_speed", ShadowState.HAPPY, ShadowState.NIL)
```

测试文件: `tests/unit/test_cnc_twin.py`

```python
def test_cnc_simulate_idle():
    """IDLE 状态仿真输出全零（除温度和功率待机值）"""
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.IDLE
    out = cnc.simulate(1.0)
    assert out["spindle_speed"] == 0
    assert out["spindle_load"] == 0
    assert out["feed_rate"] == 0
    assert out["coolant_flow"] == 0.0

def test_cnc_simulate_run_reaches_target_rpm():
    """RUN 状态下主轴加速到目标转速"""
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.RUN
    cnc.current_program = "PART-A_OP1.nc"
    # 运行足够长时间达到稳态
    for _ in range(500):
        out = cnc.simulate(0.1)
    assert 7500 < out["spindle_speed"] < 8500  # 接近 8000 rpm

def test_cnc_simulate_alarm_estop():
    """ALARM 状态下主轴停转，温度下降"""
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.RUN
    cnc.current_program = "test.nc"
    for _ in range(200):
        cnc.simulate(0.1)  # 达到稳态
    cnc._state = CNCState.ALARM
    cnc.current_program = None
    for _ in range(1000):
        out = cnc.simulate(0.1)
    assert out["spindle_speed"] == 0
    assert out["temperature"] < 30.0  # 冷却到接近环境温度

def test_cnc_tool_wear_accumulation():
    """长时间运行后刀具寿命下降"""
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.RUN
    cnc.current_program = "test.nc"
    initial_life = cnc.tool_life[0]
    for _ in range(10000):
        cnc.simulate(0.1)
    assert cnc.tool_life[0] < initial_life

def test_cnc_ode_numerical_stability_rk4():
    """RK4 积分在急停工况下不发散"""
    cnc = CNCTwin("CNC-001", "ns=2;s=CNC-001")
    cnc._state = CNCState.RUN
    cnc.current_program = "test.nc"
    for _ in range(200):
        cnc.simulate(0.1)  # 达到稳态
    # 模拟急停：瞬间切到 ALARM
    cnc._state = CNCState.ALARM
    cnc.current_program = None
    # 大步长也不会发散
    out = cnc.simulate(1.0)
    assert out["temperature"] > 0  # 温度不会变成负数
    assert out["spindle_speed"] == 0
```

测试文件: `tests/unit/test_robot_agv_warehouse.py`

```python
def test_robot_simulate_idle():
    """机器人 IDLE 状态 TCP 速度为 0"""
    rob = RobotTwin("ROB-001", "ns=2;s=ROB-001")
    out = rob.simulate(1.0)
    assert out["tcp_speed"] == 0.0
    assert out["grip_state"] == False

def test_robot_joint_limit_validation():
    """关节角度超限时验证失败"""
    rob = RobotTwin("ROB-001", "ns=2;s=ROB-001")
    result = rob.sync_from_physical({"joint_angles": [200, 0, 0, 0, 0, 0]})  # J1 > 180+5
    assert result is False

def test_agv_battery_drain():
    """移动状态下电池消耗"""
    agv = AGVTwin("AGV-001", "ns=2;s=AGV-001")
    agv._state = AGVState.MOVE
    initial = agv.battery
    agv.simulate(100.0)
    assert agv.battery < initial

def test_agv_needs_charge():
    """电池低于 20% 时 needs_charge 返回 True"""
    agv = AGVTwin("AGV-001", "ns=2;s=AGV-001")
    agv.battery = 15.0
    assert agv.needs_charge() is True

def test_warehouse_store_and_retrieve():
    """入库后库存增加，出库后减少"""
    wh = WarehouseTwin()
    wh.store_request("PART-A", quantity=5)
    # 手动推进堆垛机任务完成
    wh._current_task_time = 0
    wh.task_queue[0]["duration"] = 0
    wh.simulate(0.1)
    assert wh.part_a_stock == 5
    wh.retrieve_request("PART-A", quantity=2)
    wh.task_queue[0]["duration"] = 0
    wh.simulate(0.1)
    assert wh.part_a_stock == 3

def test_warehouse_full_state():
    """库存超 95% 时状态变为 FULL"""
    wh = WarehouseTwin()
    wh.part_a_stock = 191  # 191/200 = 95.5%
    wh.simulate(0.1)
    assert wh._state == WarehouseState.FULL
```

测试文件: `tests/unit/test_reward_calculator.py`

```python
def test_reward_throughput_part_a():
    """完成 PART-A 获得 10 分"""
    calc = RewardCalculator()
    orders = [Order("O1", "PART-A", "OP10", "prog.nc", completed=True)]
    r = calc.compute({}, orders, {}, 0)
    assert r == 10.0

def test_reward_throughput_part_b():
    """完成 PART-B 获得 8 分"""
    calc = RewardCalculator()
    orders = [Order("O1", "PART-B", "OP10", "prog.nc", completed=True)]
    r = calc.compute({}, orders, {}, 0)
    assert r == 8.0

def test_reward_balance_penalty():
    """设备利用率不均衡时扣分"""
    calc = RewardCalculator()
    metrics = {"CNC-001_util": 1.0, "CNC-002_util": 0.0, "CNC-003_util": 0.0}
    r = calc.compute(metrics, [], {}, 0)
    assert r < 0  # 纯惩罚

def test_reward_delay_penalty():
    """逾期订单扣分"""
    calc = RewardCalculator()
    order = Order("O1", "PART-A", "OP10", "prog.nc", due_time=100.0)
    r = calc.compute({}, [order], {"time": 200.0}, 0)
    assert r < 0  # 逾期 100s × 0.1 = -10

def test_reward_no_double_count():
    """同一订单不会重复给奖励"""
    calc = RewardCalculator()
    order = Order("O1", "PART-A", "OP10", "prog.nc", completed=True, _rewarded=True)
    r = calc.compute({}, [order], {}, 0)
    assert r == 0.0  # 已 rewarded，不重复
```

测试文件: `tests/unit/test_circuit_breaker.py`

```python
def test_circuit_breaker_closed_normal():
    """CLOSED 状态下请求正常通过"""
    cb = CircuitBreaker(failure_threshold=3, timeout=5.0)
    assert cb.state == "CLOSED"
    assert cb.allow_request() is True

def test_circuit_breaker_opens_after_n_failures():
    """连续 N 次失败后切换到 OPEN"""
    cb = CircuitBreaker(failure_threshold=3, timeout=5.0)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.allow_request() is False

def test_circuit_breaker_half_open_after_timeout():
    """OPEN 状态超时后进入 HALF_OPEN，允许探测请求"""
    cb = CircuitBreaker(failure_threshold=3, timeout=1.0)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == "OPEN"
    time.sleep(1.1)
    assert cb.allow_request() is True
    assert cb.state == "HALF_OPEN"

def test_circuit_breaker_resets_on_success():
    """HALF_OPEN 状态下成功后回到 CLOSED"""
    cb = CircuitBreaker(failure_threshold=3, timeout=1.0)
    for _ in range(3):
        cb.record_failure()
    time.sleep(1.1)
    cb.allow_request()  # → HALF_OPEN
    cb.record_success()
    assert cb.state == "CLOSED"

def test_circuit_breaker_reopens_on_half_open_failure():
    """HALF_OPEN 状态下失败后重新 OPEN"""
    cb = CircuitBreaker(failure_threshold=3, timeout=1.0)
    for _ in range(3):
        cb.record_failure()
    time.sleep(1.1)
    cb.allow_request()  # → HALF_OPEN
    cb.record_failure()
    assert cb.state == "OPEN"
```

测试文件: `tests/unit/test_manufacturing_env.py`

```python
def test_factorized_action_dispatch():
    """factorized action (device_idx, task_idx) 正确分配任务"""
    env = make_test_env()  # helper: 注册 7 个孪生 + 5 个待处理订单
    obs = env.reset()
    # action = device_idx * n_tasks_max + task_idx
    action = 0 * 20 + 0  # CNC-001 + 第一个任务
    obs, reward, done, info = env.step(action)
    assert info.get("dispatched") is not None

def test_action_no_idle_device():
    """所有设备忙碌时，任何 assign 动作无效"""
    env = make_test_env()
    # 把所有 CNC 设为 RUN
    for dev_id in ["CNC-001", "CNC-002", "CNC-003"]:
        env.dt.get(dev_id)._state = CNCState.RUN
    obs, reward, done, info = env.step(0)  # 尝试分配
    assert info.get("dispatched") is None

def test_done_on_all_completed():
    """所有订单完成后 done=True"""
    env = make_test_env(orders=[])
    obs = env.reset()
    # 手动标记完成
    env.completed = env.order_queue[:]
    obs, reward, done, info = env.step(6)  # WAIT
    assert done is True

def test_done_on_max_steps():
    """超过最大步数后 done=True"""
    env = make_test_env()
    env.reset()
    env._step_count = 999
    obs, reward, done, info = env.step(6)
    assert done is True
```

测试文件: `tests/integration/test_mode_switch.py`

```python
def test_sim_to_prod_no_state_loss():
    """从仿真切换到生产模式不丢失状态"""
    manager = DigitalTwinManager()
    register_all_twins(manager)
    manager.set_mode("simulation")
    manager.simulate_all(10.0)
    sim_report = manager.all_health_reports()
    manager.set_mode("production")
    # 不应抛出异常
    prod_report = manager.all_health_reports()
    # 设备 ID 集合一致
    assert set(sim_report.keys()) == set(prod_report.keys())

def test_verify_consistency_catches_drift():
    """verify_consistency 正确检测 20% 以上的偏差"""
    manager = DigitalTwinManager()
    sim_data = {"CNC-001": {"spindle_speed": 8000}}
    real_data = {"CNC-001": {"spindle_speed": 5000}}  # 37.5% 偏差
    discrepancies = manager.verify_consistency(sim_data, real_data)
    assert len(discrepancies) == 1
    assert "CNC-001.spindle_speed" in discrepancies[0]
```

测试文件: `tests/unit/test_dataclasses.py`

```python
def test_order_default_values():
    """Order dataclass 默认值正确"""
    o = Order("O1", "PART-A", "OP10", "prog.nc")
    assert o.completed is False
    assert o._rewarded is False
    assert o.assigned_device is None

def test_order_tuple_unpacking():
    """Order 支持 tuple unpacking（target_pose）"""
    o = Order("O1", "PART-A", "OP10", "prog.nc", target_pose=(100.0, 200.0, 300.0, 0, 0, 0))
    assert len(o.target_pose) == 6
```

### 11.10 测试计划汇总

| 测试文件 | 用例数 | 覆盖模块 | 类型 |
|----------|--------|---------|------|
| test_data_shadow.py | 5 | DataShadow | 单元 |
| test_sync_from_physical.py | 6 | DigitalTwinBase + callback | 单元 |
| test_cnc_twin.py | 5 | CNCTwin (ODE + 刀具 + 状态) | 单元 |
| test_robot_agv_warehouse.py | 6 | RobotTwin + AGVTwin + WarehouseTwin | 单元 |
| test_reward_calculator.py | 5 | RewardCalculator | 单元 |
| test_circuit_breaker.py | 5 | CircuitBreaker | 单元 |
| test_manufacturing_env.py | 4 | ManufacturingEnv (action + done) | 单元 |
| test_mode_switch.py | 2 | DigitalTwinManager 模式切换 | 集成 |
| test_dataclasses.py | 2 | Order dataclass | 单元 |
| **已有 3 个** | 3 | sync/simulate 一致性 + 策略迁移 | 集成 |
| **合计** | **43** | | |

---

## 第九章：工业安全架构

### 9.1 Purdue 模型分层

```
┌──────────────────────────────────────────────────────────────┐
│ Level 5: Enterprise Cloud    │ 云 ERP, 大数据分析 (可选)     │
│ ──────────────────────────────────────────────────────────── │
│ Level 4: Enterprise Network  │ SAP S/4HANA, 邮件, 文件服务器  │
│   Subnet: 10.0.4.0/24       │ VPN Gateway → 远程访问         │
├──────────────────────────────────────────────────────────────┤
│           ═══════ DMZ Firewall ═══════                       │
├──────────────────────────────────────────────────────────────┤
│ Level 3.5: DMZ               │ MES Web UI + API Gateway      │
│   Subnet: 192.168.50.0/24    │ OPC UA Reverse Proxy          │
│   ┌────────────────────────┐ │ PostgreSQL Mirror (只读)       │
│   │ OPC UA 反向代理         │ │ 历史数据服务器                  │
│   │ (终止外部连接,证书验证) │ │                                │
│   └────────────────────────┘ │                                │
├──────────────────────────────────────────────────────────────┤
│           ═══════ OT Firewall ═══════                       │
├──────────────────────────────────────────────────────────────┤
│ Level 3: Manufacturing Ops  │ MES Server (主)                │
│   Subnet: 192.168.10.0/24   │ OPC UA Client + RL Scheduler   │
│                             │ SCADA Server (WinCC)           │
│                             │ Database Server (PG+Timescale) │
│                             │ 工程师站 / HMI                  │
├──────────────────────────────────────────────────────────────┤
│ Level 2: Supervisory Ctrl   │ OPC UA Server                  │
│   Subnet: 192.168.20.0/24   │ HMI Panels                     │
│                             │ RTU / 数据集中器                 │
├──────────────────────────────────────────────────────────────┤
│ Level 1: Basic Control      │ PLC 机架 (Siemens S7-1500)     │
│   Subnet: 192.168.30.0/24   │ 安全 PLC (急停逻辑)             │
│                             │ 驱动器 (VFD / Servo)            │
├──────────────────────────────────────────────────────────────┤
│ Level 0: Field Devices      │ 传感器、编码器、RFID            │
│   (无IP, 现场总线)          │ 执行器、阀岛、安全光幕            │
│                             │ Profibus / EtherCAT / IO-Link  │
└──────────────────────────────────────────────────────────────┘

网络隔离规则:
- Level 4 → Level 3: 仅允许 MES API (HTTPS 443) + OPC UA 反向代理 (4840)
- Level 3 → Level 2: 仅允许 OPC UA (4840) + Modbus TCP (502) + S7Comm (102)
- Level 2 → Level 1: 仅允许 OPC UA (4840) + 工程下载 (102)
- DMZ → Level 3: 仅允许 PostgreSQL 流复制 (5432)
- 所有跨层流量经过 IDS 检测 (Snort/Suricata)
```

### 9.2 OPC UA 安全策略配置

```yaml
# OPC UA Server 安全配置
SecurityPolicies:
  - None:                    # 仅调试用, 生产环境禁用
      enabled: false
  - Basic128Rsa15:
      enabled: false         # 已废弃 (SHA-1)
  - Basic256:
      enabled: false         # 已废弃
  - Basic256Sha256:
      enabled: true
      min_key_length: 2048
      sign: true
      encrypt: true
  - Aes128_Sha256_RsaOaep:   # 推荐 (主流客户端支持)
      enabled: true
  - Aes256_Sha256_RsaPss:    # 最高安全等级
      enabled: true

UserAuthentication:
  - Anonymous: false         # 禁止匿名访问
  - UserPassword:
      enabled: true
      password_policy:
        min_length: 12
        require_special: true
        require_digit: true
  - Certificate:
      enabled: true
      trusted_issuers: ["CN=SMDS-Enterprise-CA"]

SessionSettings:
  session_timeout: 3600      # 1h 无操作自动断开
  max_sessions_per_user: 3
  audit_log: true            # 记录所有连接/断开/方法调用
```

### 9.3 访问控制矩阵

| 角色 | 读设备状态 | 写设备参数 | 调用方法 | 管理用户 | 查看审计日志 |
|------|:--:|:--:|:--:|:--:|:--:|
| Operator (操作员) | ✅ | ❌ | Start/Stop/Pause | ❌ | ❌ |
| Maintenance (维修工) | ✅ | 参数(限) | Start/Stop/ResetAlarm | ❌ | ❌ |
| Engineer (工程师) | ✅ | ✅ | ✅ | ❌ | ✅ |
| Scheduler (调度系统) | ✅ | ✅ | Start/Stop | ❌ | ❌ |
| Admin (管理员) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Auditor (审计员) | ❌ | ❌ | ❌ | ❌ | ✅ |

### 9.4 入侵检测规则示例

```snort
# Snort/Suricata IDS 规则 — 工控协议异常检测

# 检测: 对 OPC UA 端口的非 OPC UA 流量
alert tcp any any -> $OT_NET 4840 (msg:"OPC UA: Non-UA traffic on 4840";
    flow:to_server,established;
    content:!"HEL"; depth:3;
    sid:1000001; rev:1;)

# 检测: 异常多的订阅请求 (可能的 DoS)
alert tcp any any -> $OT_NET 4840 (msg:"OPC UA: Excessive Subscriptions";
    flow:to_server,established;
    content:"|05 00 00|"; depth:3;
    threshold:type threshold, track by_src, count 50, seconds 10;
    sid:1000002; rev:1;)

# 检测: Modbus 功能码扫描
alert tcp any any -> $OT_NET 502 (msg:"Modbus: Function code scan suspected";
    flow:to_server,established;
    content:"|00|"; offset:7; depth:1;
    detection_filter:track by_src, count 10, seconds 5;
    sid:1000003; rev:1;)
```

---

## 第十章：系统演化路线图

### Phase 1 — 基础连接 (Week 1-4): "让设备说话"

**目标:** 建立 OPC UA 地址空间 + 基础数据采集

| 交付物 | 描述 | 验收标准 |
|--------|------|---------|
| OPC UA Server 部署 | 在工业 PC 上部署 OPC UA Server (open62541) | 所有 7 个设备 NodeId 可通过 UaExpert 浏览 |
| PLC 通信适配器 | Modbus TCP → OPC UA 桥接 | CNC-001 主轴转速数据实时推送, 延迟 < 500ms |
| 基础数据采集器 | Python 异步 OPC UA Client, 写入 CSV | 7 设备 × 40 变量 × 1Hz = 持续 4h 无中断 |
| 地址空间文档 | 生成的 NodeSet2.xml + 人工注释 | 每个节点有描述和工程单位 |

**Phase 1 架构:**
```
PLC(s) ──Modbus──→ OPC UA Server ──Subscription──→ CSV Logger
                         │
                    UaExpert (调试)
```

### Phase 2 — 数字孪生核心 (Week 5-8): "让虚拟世界活起来"

**目标:** Python 数字孪生类 + 实时同步 + 基础可视化

| 交付物 | 描述 | 验收标准 |
|--------|------|---------|
| 数字孪生类库 | CNCTwin, RobotTwin, AGVTwin, WHTwin + DataShadow | 所有类通过单元测试, 仿真模式产生合理数据 |
| DigitalTwinManager | 统一管理 7 个孪生实例, 批量同步 | sync_all() 完成 7 设备 < 100ms |
| TimescaleDB 存储 | 安装配置 PG+TimescaleDB, 数据影子持久化 | 560 点/s 写入, 查询 24h 数据 < 1s |
| 基础 Dashboard | Streamlit Web 界面, 设备状态 + 实时折线图 | 操作员可查看所有设备状态和传感器趋势 |
| 报警推送 | AlarmManager 检测异常 → WebSocket 推送 → HMI 弹窗 | 报警延迟 < 2s |

**Phase 2 架构:**
```
OPC UA Server ──→ OPCUAConnector ──→ DigitalTwinManager
                                          │
                              ┌───────────┼───────────┐
                              │           │           │
                         CNCTwin     RobotTwin    AGVTwin
                              │           │           │
                              └───────────┼───────────┘
                                          │
                                    TimescaleDB
                                          │
                                    Streamlit UI
```

### Phase 3 — 智能调度 (Week 9-14): "让系统学会决策"

**目标:** RL 调度引擎 + MES 完整交互序列

| 交付物 | 描述 | 验收标准 |
|--------|------|---------|
| ManufacturingEnv | 车间仿真环境, 7 设备 × 2 产品 | 与 DigitalTwinManager 集成, 可 reset/step |
| Double DQN 训练 | 50000 episodes 训练 | Makespan 比 FIFO 规则 < 85% |
| MES Ordnance 管理 | 订单创建、工序展开、工单分配 | 支持 2 产品 × 4 工序的完整流程 |
| 规则引擎 (降级) | SPT + EDD + FIFO 组合规则 | RL 不可用时自动切换 |
| 调度 Dashboard | 甘特图 + Q值热力图 + 设备利用率 | 实时更新, 可回溯历史决策 |

**Phase 3 架构:**
```
MES OrderManager ──→ ManufacturingEnv ──→ DQN Scheduler
       │                    │                    │
       │              DigitalTwinManager ←───────┘
       │                    │
       └────────────────────┴──→ TimescaleDB → Dashboard
```

### Phase 4 — 安全加固与运维 (Week 15-18): "让系统可信赖"

**目标:** Purdue 安全架构 + 冗余 + 文档

| 交付物 | 描述 | 验收标准 |
|--------|------|---------|
| 网络分区 | VLAN 划分 + 防火墙规则 + DMZ 部署 | 扫描测试: L3→L2 仅 OPC UA 4840 可达 |
| OPC UA 安全加固 | 证书认证 + Sign&Encrypt + 审计日志 | 安全扫描 0 Critical/High |
| IDS 部署 | Suricata + 工控规则集 | 模拟攻击检测: Modbus 扫描 + OPC UA 暴力破解 |
| 高可用 | OPC UA Server 主备 + DB 流复制 | 主节点故障切换 < 30s |
| 完整文档 | ADR 7 篇 + 故障分析 10 场景 + API 文档 + 运维手册 | 新入职工程师可独立部署 Phase 1 |
| 验收测试 | 端到端集成测试 | 48h 连续运行, 数据丢失 < 0.01%, 调度可用率 > 99.5% |

**完成架构 (Phase 4):**
```
                  ┌─────────────┐
                  │  Cloud ERP  │ (可选)
                  └──────┬──────┘
                         │ VPN
                  ═══ DMZ ═══════
                  ┌──────┴──────┐
                  │ OPC UA Rev  │
                  │   Proxy     │
                  │ PG Mirror   │
                  └──────┬──────┘
                  ═══ OT FW ════
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────┴────┐     ┌─────┴─────┐    ┌─────┴─────┐
   │MES (主) │     │MES (备)   │    │  SCADA    │
   └────┬────┘     └───────────┘    └───────────┘
        │
   ┌────┴──────────────────────────┐
   │   OPC UA Server (主/备)       │
   │   VRIP: 192.168.20.10         │
   └────┬──────────────────────────┘
        │
   ┌────┴────┬──────┬──────┬──────┐
   │ PLC-001 │PLC-002│PLC-003│SafePLC│
   └────┬────┴──────┴──────┴──────┘
        │
   ┌────┴──────────────────────┐
   │ CNC-001..003  ROB-001..002│
   │ AGV-001       WH-001      │
   └────────────────────────────┘
```

---

## 附录 A: 技术栈总览

| 层次 | 技术选型 | 用途 |
|------|---------|------|
| 设备通信 | OPC UA (open62541 / python-opcua) | 设备建模 + 数据采集 + 方法调用 |
| 数字孪生 | Python 3.12 + asyncio | 孪生类定义, 数据同步, 仿真 |
| 机器学习 | PyTorch 2.x + NumPy | DQN 训练, 状态编码 |
| 业务数据库 | PostgreSQL 16 + TimescaleDB 2.x | 订单、工单、库存 + 时序数据 |
| 可视化 | Streamlit / Grafana | 设备仪表板, 时序图表 |
| 消息推送 | MQTT (Mosquitto) / WebSocket | 报警实时推送 |
| 安全 | Suricata IDS + OPC UA 证书 | 入侵检测 + 安全通信 |
| 部署 | Docker + Docker Compose | 容器化部署 |
| 版本控制 | Git + GitHub (23xxCh/digital-system) | 源代码管理 |

## 附录 B: 开发环境搭建

```bash
# 1. Python 依赖
pip install opcua-asyncio asyncua numpy torch streamlit
pip install sqlalchemy psycopg2 timescaledb
pip install paho-mqtt websockets

# 2. 数据库
docker run -d --name timescaledb \
  -e POSTGRES_PASSWORD=smds2026 \
  -p 5432:5432 \
  timescale/timescaledb:latest-pg16

# 3. OPC UA Server 模拟器 (开发用)
docker run -d --name opcua-simulator \
  -p 4840:4840 \
  opcua/simulator:latest

# 4. 启动数字孪生管理
python -m smds.digital_twin.manager --config config/production.yaml
```

## 附录 C: 目录结构 (规划)

```
digital-system/
├── CONTEXT.md
├── CLAUDE.md
├── docs/
│   ├── adr/                    # 架构决策记录
│   │   ├── 001-opcua-over-mqtt.md
│   │   ├── 002-python-async.md
│   │   ├── 003-double-dqn.md
│   │   ├── 004-purdue-security.md
│   │   ├── 005-postgres-timescale.md
│   │   ├── 006-data-shadow.md
│   │   └── 007-json-over-binary.md
│   └── agents/                 # Agent 技能配置
│       ├── backlog.md
│       ├── triage-labels.md
│       └── domain.md
├── src/
│   └── smds/                   # Smart Mfg Digital System
│       ├── opcua/              # OPC UA 连接器
│       ├── digital_twin/       # 数字孪生类
│       ├── mes/                # MES 业务逻辑
│       ├── scheduler/          # RL 调度引擎
│       ├── security/           # 安全模块
│       └── web/                # Web Dashboard
├── config/
│   ├── production.yaml
│   ├── development.yaml
│   └── security_policies.yaml
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── simulations/                # 训练用仿真数据
└── docker/
    └── docker-compose.yml
```

---

> 文档版本: v1.1 | 生成日期: 2026-05-02 | 作者: cxx450 + Claude Opus 4.7  
> 许可证: MIT | 仓库: https://github.com/23xxCh/digital-system

---

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | 代码与仿真架构 | 2 | CLEAR | 4 proposals, 4 accepted, 0 deferred |
| Eng Review | `/plan-eng-review` | 架构+代码+测试+性能 | 1 | CLEAR | 9 issues found, 0 critical gaps |
| Outside Voice | Claude subagent | 独立挑战 | 1 | CLEAR | 7 findings, 2 tension points resolved |

- **UNRESOLVED:** 0
- **VERDICT:** CEO + ENG CLEARED — 可以开始实现

### 工程审查决策

| # | 问题 | 严重度 | 决策 | 理由 |
|---|------|--------|------|------|
| 1 | ManufacturingEnv 职责过多 | P2 | 拆分为 3 类 | 单一职责，可独立测试 |
| 2 | 动作空间太粗糙(8个) | P1 | Factorized (device×task) | 能表达真实调度决策 |
| 3 | OPC UA 无 CircuitBreaker | P2 | 添加 CircuitBreaker | 防止慢响应拖垮系统 |
| 4 | isinstance 散布 4+ 处 | P2 | 多态分发 | 新设备不改多文件 |
| 5 | Euler 积分不稳定 | P2 | 换 RK4 | 急停工况不发散 |
| 6 | Shadow 变化无回调 | P3 | 添加 on_shadow_transition | 生产可观测性 |
| 7 | 魔法数字散布 | P3 | 提取为 Config dataclass | 可调参 |
| 8 | latest_happy() 线性扫描 | P3 | 缓存 latest_happy | O(1) 查找 |
| 9 | ODE 子步长过细 | P3 | 放宽到 50ms | 减少计算量 5x |

### Outside Voice 发现

| # | 发现 | 张力 | 解决 |
|---|------|------|------|
| 1 | 训练安全沙箱缺失 | 工程审查未涉及 | ACCEPTED → 添加 SafetyGuard |
| 2 | ODE 标定数据从何而来 | 部分张力 | 参考设计定位，教学价值保留 |
| 3 | DQN 状态空间未严格定义 | 部分张力 | 67 维已定义，shadow 映射待补 |
| 4 | 无实际可运行代码 | 无张力 | 4 阶段路线图已覆盖 |
| 5 | 故障场景缺 FMEA 评分 | 工程审查未涉及 | ACCEPTED → 补充 RPN |
| 6 | OPC UA 安全实现细节缺失 | 无张力 | Phase 4 覆盖 |
| 7 | 战略模糊 | 无张力 | CEO 审查已确认参考设计定位 |

### 新增内容（本次审查）
- 11.9: 完整测试用例（22 个缺口补充，总计 43 个）
- 11.10: 测试计划汇总表
- 训练安全沙箱（SafetyGuard）— 待实现
- FMEA 评分补充 — 待实现
- CircuitBreaker 类设计 — 待实现
- 多态分发接口（is_idle/can_accept_task/assign_task）— 待实现
- latest_happy 缓存 — 待实现
