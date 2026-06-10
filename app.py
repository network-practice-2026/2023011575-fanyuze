import sqlite3
import os
import math
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'network_kb.db')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            layer TEXT NOT NULL,
            function TEXT,
            protocols TEXT,
            devices TEXT,
            knowledge TEXT NOT NULL
        )
    ''')

    count = db.execute('SELECT COUNT(*) FROM knowledge_points').fetchone()[0]
    if count == 0:
        seed_data = [
            # === 应用层 ===
            ('应用层', '为应用进程提供网络通信服务，定义应用进程间通信规则',
             'HTTP,HTTPS', 'Web浏览器,Web服务器',
             'HTTP是超文本传输协议，用于从Web服务器传输超文本到本地浏览器的协议，默认端口80。HTTPS是HTTP的安全版本，使用SSL/TLS加密传输，默认端口443。HTTP请求方法包括GET、POST、PUT、DELETE等。'),
            ('应用层', '为应用进程提供网络通信服务，定义应用进程间通信规则',
             'DNS', 'DNS服务器',
             'DNS（域名系统）将域名解析为IP地址。解析过程：客户端向本地DNS发起查询，若缓存命中则直接返回；未命中则经根DNS→顶级DNS→权威DNS递归或迭代查询，最终返回IP地址。DNS默认使用UDP端口53。'),
            ('应用层', '为应用进程提供网络通信服务，定义应用进程间通信规则',
             'FTP', 'FTP客户端,FTP服务器',
             'FTP（文件传输协议）使用两个连接：控制连接（端口21）发送命令，数据连接（端口20）传输文件数据。支持主动模式（服务器主动连接客户端）和被动模式（客户端主动连接服务器）。'),
            ('应用层', '为应用进程提供网络通信服务，定义应用进程间通信规则',
             'SMTP,POP3,IMAP', '邮件客户端,邮件服务器',
             '电子邮件系统三大协议：SMTP（发送邮件，端口25/587）、POP3（下载邮件到本地，端口110）、IMAP（在线管理邮件，端口143）。SMTP通过MTA（邮件传输代理）逐步转发邮件到目标服务器。'),
            ('应用层', '为应用进程提供网络通信服务，定义应用进程间通信规则',
             'DHCP', 'DHCP服务器,客户端',
             'DHCP（动态主机配置协议）自动分配IP地址、子网掩码、默认网关、DNS服务器等。四步交互：客户端发送DHCP Discover广播→服务器响应DHCP Offer→客户端发送DHCP Request→服务器确认DHCP ACK。'),
            ('应用层', '为应用进程提供网络通信服务，定义应用进程间通信规则',
             'Telnet,SSH', '远程主机,终端',
             'Telnet（端口23）提供远程登录服务但明文传输不安全。SSH（安全外壳协议，端口22）提供加密的远程登录通道，支持密码和密钥认证，广泛用于服务器管理。'),
            # === 传输层 ===
            ('传输层', '提供端到端的数据传输服务，实现进程间逻辑通信',
             'TCP', 'TCP报文段',
             'TCP（传输控制协议）提供面向连接、可靠的数据传输。通过三次握手建立连接（SYN→SYN-ACK→ACK），四次挥手释放连接（FIN→ACK→FIN→ACK）。使用序列号、确认号和校验和保证数据有序无误到达。'),
            ('传输层', '提供端到端的数据传输服务，实现进程间逻辑通信',
             'UDP', 'UDP数据报',
             'UDP（用户数据报协议）提供无连接、不可靠的传输服务。无握手过程，直接发送数据，开销小速度快，适用于实时应用（视频直播、在线游戏、VoIP）和DNS查询等简单请求-响应场景。'),
            ('传输层', '提供端到端的数据传输服务，实现进程间逻辑通信',
             '端口号,套接字', '端口',
             '端口号标识主机上的具体应用进程，范围0~65535。知名端口0~1023（HTTP:80, HTTPS:443, DNS:53, SSH:22），注册端口1024~49151，动态端口49152~65535。套接字=IP地址+端口号。'),
            ('传输层', '提供端到端的数据传输服务，实现进程间逻辑通信',
             'TCP流量控制', '滑动窗口',
             'TCP使用滑动窗口机制进行流量控制。接收方通过TCP头部窗口字段告知发送方剩余缓冲区大小。发送方根据窗口大小调整发送速率，防止接收方被数据淹没。窗口大小可动态变化。'),
            ('传输层', '提供端到端的数据传输服务，实现进程间逻辑通信',
             'TCP拥塞控制', '拥塞窗口CWND',
             'TCP拥塞控制包含四种算法：慢启动（指数增长CWND）、拥塞避免（线性增长）、快速重传（收到3个重复ACK立即重传）、快速恢复（不进入慢启动）。通过CWND和ssthresh动态控制发送速率。'),
            # === 网络层 ===
            ('网络层', '负责将数据包从源主机路由到目的主机，实现逻辑寻址和路由选择',
             'IP', '路由器,IP数据包',
             'IP（互联网协议）是网络层核心协议。IPv4地址为32位（4字节），分A/B/C/D/E类。IPv6地址为128位（16字节），解决IPv4地址枯竭。IP数据包头部包含源IP、目的IP、TTL、协议类型等字段。'),
            ('网络层', '负责将数据包从源主机路由到目的主机，实现逻辑寻址和路由选择',
             '路由协议(RIP,OSPF,BGP)', '路由器,路由表',
             'RIP（距离向量协议，最大跳数15，适合小型网络）。OSPF（链路状态协议，使用Dijkstra算法计算最短路径，适合大型企业网络）。BGP（路径向量协议，互联网骨干路由协议，基于AS路径选择）。'),
            ('网络层', '负责将数据包从源主机路由到目的主机，实现逻辑寻址和路由选择',
             'ICMP', 'ICMP报文',
             'ICMP（互联网控制报文协议）用于报告网络错误和诊断信息。封装在IP数据包中。Ping使用ICMP Echo Request/Reply测试连通性；Traceroute利用TTL超时和ICMP Time Exceeded追踪数据包路径。'),
            ('网络层', '负责将数据包从源主机路由到目的主机，实现逻辑寻址和路由选择',
             '子网划分,CIDR', '子网掩码',
             'CIDR（无类别域间路由）使用斜杠表示法如192.168.1.0/24。子网掩码将IP分为网络位和主机位。VLSM（可变长子网掩码）允许不同子网使用不同的子网掩码，提高地址利用率。'),
            ('网络层', '负责将数据包从源主机路由到目的主机，实现逻辑寻址和路由选择',
             'NAT', 'NAT路由器',
             'NAT（网络地址转换）将私有IP映射为公有IP，实现多设备共享上网。静态NAT一对一映射，动态NAT从地址池分配，PAT/NAPT（端口地址转换）一对多映射（最常用）。私有地址段：10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16。'),
            # === 数据链路层 ===
            ('数据链路层', '在物理层之上提供可靠的帧传输，实现介质访问控制和差错检测',
             'MAC地址', '网卡,交换机',
             'MAC地址（媒体访问控制地址）是48位（6字节）的物理地址，全球唯一。前24位为OUI（组织唯一标识符），后24位由厂商分配。以十六进制表示如00:1A:2B:3C:4D:5E。用于局域网内帧的寻址。'),
            ('数据链路层', '在物理层之上提供可靠的帧传输，实现介质访问控制和差错检测',
             'ARP', 'ARP表',
             'ARP（地址解析协议）用于将IP地址解析为MAC地址。主机广播ARP Request（目的MAC=FF:FF:FF:FF:FF:FF）查询目标IP对应的MAC，目标主机单播回复ARP Reply。ARP表缓存IP-MAC映射。'),
            ('数据链路层', '在物理层之上提供可靠的帧传输，实现介质访问控制和差错检测',
             '以太网交换机', '交换机,交换表',
             '交换机是数据链路层设备，根据MAC地址转发帧。工作原理：学习源MAC→查交换表→已知目的MAC则定向转发，未知则泛洪。交换表（MAC地址表）记录MAC-端口映射，有老化时间。支持全双工通信。'),
            ('数据链路层', '在物理层之上提供可靠的帧传输，实现介质访问控制和差错检测',
             '以太网帧格式', '以太网帧',
             '以太网帧结构：前导码(7B)+帧起始定界符(1B)+目的MAC(6B)+源MAC(6B)+类型/长度(2B)+数据(46~1500B)+FCS帧校验(4B)。MTU为1500字节，小于46字节需填充。FCS使用CRC-32校验。'),
            ('数据链路层', '在物理层之上提供可靠的帧传输，实现介质访问控制和差错检测',
             'VLAN', 'VLAN交换机',
             'VLAN（虚拟局域网）将一个物理局域网逻辑划分为多个广播域。基于IEEE 802.1Q标准，在以太网帧中插入4字节VLAN标签（含VLAN ID，范围1~4094）。Trunk端口承载多个VLAN流量。'),
            # === 物理层 ===
            ('物理层', '定义物理设备之间的接口标准，传输原始比特流',
             '双绞线', '双绞线,RJ-45接口',
             '双绞线是最常用的传输介质，两根绝缘铜线绞合以减少电磁干扰。UTP（非屏蔽双绞线）和STP（屏蔽双绞线）。类别规格：Cat5e(100MHz/100m)、Cat6(250MHz)、Cat6a(500MHz)、Cat7(600MHz)。使用RJ-45接头。'),
            ('物理层', '定义物理设备之间的接口标准，传输原始比特流',
             '光纤', '光纤,光模块(SFP)',
             '光纤利用光全反射原理传输数据，抗电磁干扰、传输距离远。单模光纤芯径约9μm，使用激光源，传输距离可达数十/上百公里。多模光纤芯径50/62.5μm，使用LED光源，传输距离数百米。'),
            ('物理层', '定义物理设备之间的接口标准，传输原始比特流',
             '集线器', '集线器Hub',
             '集线器是物理层设备，将接收的信号复制到所有其他端口（广播式转发）。所有端口共享带宽，属同一冲突域。半双工通信。集线器已被交换机基本取代，仅在老旧网络或特殊场景中使用。'),
            ('物理层', '定义物理设备之间的接口标准，传输原始比特流',
             '信号编码（曼彻斯特编码）', '编码器',
             '曼彻斯特编码在每比特中间产生跳变：高到低=1，低到高=0。自带时钟信号，便于同步。差分曼彻斯特编码：位边界有跳变=0，无跳变=1。以太网10Base-T使用曼彻斯特编码。'),
            ('物理层', '定义物理设备之间的接口标准，传输原始比特流',
             '中继器,传输速率', '中继器',
             '中继器（Repeater）放大和再生衰减信号，延长传输距离。仅再生比特流，不做智能处理。传输速率从早期的10Mbps发展到如今100Gbps以上。常见以太网标准：10Base-T、100Base-TX、1000Base-T、10GBase-T。'),
        ]

        db.executemany(
            'INSERT INTO knowledge_points (layer, function, protocols, devices, knowledge) VALUES (?, ?, ?, ?, ?)',
            seed_data
        )
        db.commit()

    db.close()


def seed_data_if_empty():
    """兼容旧版：不重复插入"""
    pass


# ===================== Page Routes =====================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dns')
def dns():
    return render_template('dns.html')


@app.route('/tcp')
def tcp():
    return render_template('tcp.html')


@app.route('/scenario')
def scenario():
    return render_template('scenario.html')


@app.route('/knowledge')
def knowledge():
    return render_template('knowledge.html')


# ===================== API Routes =====================

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    layer = request.args.get('layer', '')
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))

    db = get_db()
    conditions = []
    params = []

    if layer:
        conditions.append('layer = ?')
        params.append(layer)

    if keyword:
        conditions.append('knowledge LIKE ?')
        params.append(f'%{keyword}%')

    where_clause = ''
    if conditions:
        where_clause = 'WHERE ' + ' AND '.join(conditions)

    count_query = f'SELECT COUNT(*) FROM knowledge_points {where_clause}'
    total = db.execute(count_query, params).fetchone()[0]

    offset = (page - 1) * per_page
    data_query = f'SELECT * FROM knowledge_points {where_clause} ORDER BY id LIMIT ? OFFSET ?'
    rows = db.execute(data_query, params + [per_page, offset]).fetchall()

    items = [dict(row) for row in rows]
    total_pages = max(1, math.ceil(total / per_page))

    return jsonify({
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    })


@app.route('/api/knowledge', methods=['POST'])
def add_knowledge():
    data = request.get_json()
    if not data or 'knowledge' not in data:
        return jsonify({'error': 'knowledge field is required'}), 400

    db = get_db()
    cur = db.execute(
        'INSERT INTO knowledge_points (layer, function, protocols, devices, knowledge) VALUES (?, ?, ?, ?, ?)',
        (data.get('layer', ''), data.get('function', ''),
         data.get('protocols', ''), data.get('devices', ''),
         data['knowledge'])
    )
    db.commit()

    new_id = cur.lastrowid
    row = db.execute('SELECT * FROM knowledge_points WHERE id = ?', (new_id,)).fetchone()
    return jsonify(dict(row)), 201


@app.route('/api/knowledge/<int:id>', methods=['PUT'])
def update_knowledge(id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    db = get_db()
    existing = db.execute('SELECT * FROM knowledge_points WHERE id = ?', (id,)).fetchone()
    if not existing:
        return jsonify({'error': 'Knowledge point not found'}), 404

    db.execute(
        'UPDATE knowledge_points SET layer=?, function=?, protocols=?, devices=?, knowledge=? WHERE id=?',
        (data.get('layer', existing['layer']),
         data.get('function', existing['function']),
         data.get('protocols', existing['protocols']),
         data.get('devices', existing['devices']),
         data.get('knowledge', existing['knowledge']),
         id)
    )
    db.commit()

    row = db.execute('SELECT * FROM knowledge_points WHERE id = ?', (id,)).fetchone()
    return jsonify(dict(row))


@app.route('/api/knowledge/<int:id>', methods=['DELETE'])
def delete_knowledge(id):
    db = get_db()
    existing = db.execute('SELECT * FROM knowledge_points WHERE id = ?', (id,)).fetchone()
    if not existing:
        return jsonify({'error': 'Knowledge point not found'}), 404

    db.execute('DELETE FROM knowledge_points WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted successfully'})


@app.route('/api/knowledge/graph', methods=['GET'])
def get_knowledge_graph():
    db = get_db()
    rows = db.execute(
        'SELECT DISTINCT layer, protocols, devices FROM knowledge_points ORDER BY layer'
    ).fetchall()

    node_ids = set()
    nodes = []
    links = []

    def add_node(nid, group, size=12):
        if nid not in node_ids:
            node_ids.add(nid)
            nodes.append({'id': nid, 'group': group, 'size': size})

    add_node('计算机网络', 'root', 30)

    layer_protocols = {}
    for row in rows:
        layer = row['layer']
        protocols = row['protocols']
        devices = row['devices']
        if layer not in layer_protocols:
            layer_protocols[layer] = set()
        if protocols:
            for p in protocols.split(','):
                p = p.strip()
                if p:
                    layer_protocols[layer].add(p)
        if devices:
            for d in devices.split(','):
                d = d.strip()
                if d:
                    layer_protocols[layer].add(d)

    for layer, items in layer_protocols.items():
        add_node(layer, 'layer', 20)
        links.append({'source': '计算机网络', 'target': layer})
        for item in items:
            add_node(item, 'protocol', 12)
            links.append({'source': layer, 'target': item})

    return jsonify({'nodes': nodes, 'links': links})


# ===================== Startup =====================

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
