import copy, json, os
from typing import List, Dict

COMMON = {
    # 时间戳
    "timestamp": {"type": "date"},
    # 日志大小
    "raw_size": {"type": "long"},
    # 追踪 ID
    "crid": {"type": "keyword"},
    # 追踪 来源
    "crsrc": {"type": "keyword"},
    # 环境
    "env": {"type": "keyword"},
    # 主机名
    "hostname": {"type": "keyword"},
    # 项目名
    "project": {"type": "keyword"},
    # 主题（不索引，因为都是一致的）
    "topic": {"type": "keyword", "index": False},
    # 收集服务器（不索引，因为用不上）
    "via": {"type": "keyword", "index": False},
    # 关键字
    "keyword": {"type": "text"},
    # 消息（默认不索引）
    "message": {"type": "text", "index": False},
    # 同一环境的不同部署
    "x_instance": {"type":"keyword"},
    # 目标项目
    "x_target_project": {"type": "keyword"},
    # 线程名
    "x_thread_name": {"type": "keyword"},
    # 类名
    "x_class_name": {"type": "keyword"},
    # 代码行
    "x_class_line": {"type": "long"},
    # 方法名
    "x_method_name": {"type": "keyword"},
    # 异常类名
    "x_exception_class": {"type": "keyword"},
    # 异常堆栈
    "x_exception_stack": {"type": "text"},
    # 毫秒计时
    "x_duration": {"type": "long"},
    # 主机名
    "x_host": {"type": "keyword"},
    # 特殊 HTTP 头
    "x_header_app_info": {"type": "text", "index": False},
    # 特殊 HTTP 头
    "x_header_user_token": {"type": "keyword", "index": False},
    # HTTP 方法 / SQL 方法
    "x_method": {"type": "keyword"},
    # 参数
    "x_params": {"type": "text"},
    # 路径
    "x_path": {"type": "keyword"},
    # 路径摘要
    "x_path_digest": {"type": "keyword"},
    # 查询
    "x_query": {"type": "text", "index": False},
    # 返回状态码
    "x_status": {"type": "long"},
    # IP
    "x_ip": {"type": "ip"},
    # 用户代码
    "x_user_code": {"type": "keyword"},
    # 用户姓名
    "x_user_name": {"type": "keyword"},
    # 操作
    "x_action": {"type": "keyword"},
    # 操作详情
    "x_action_detail": {"type": "text"},
    # URL
    "x_url": {"type": "keyword"},
    # 受影响的行数
    "x_affected_rows": {"type": "long"},
    # 数据库连接
    "x_database_url": {"type": "text", "index": False},
    # 数据库主机
    "x_db_host": {"type": "keyword"},
    # 数据库名
    "x_db_name": {"type": "keyword"},
    # SQL 操作
    "x_sql": {"type": "text", "index": False},
    # SQL 摘要
    "x_sql_digest": {"type": "keyword"},
    # 裸 SQL
    "x_raw_sql": {"type": "text", "index": False},
    # 等級
    "x_level": {"type": "keyword"},
    # 文件名
    "x_file": {"type": "keyword"},
    # 线程 ID
    "x_thread_id": {"type": "long"},
    # nginx 请求体发送字节数
    "x_body_bytes_sent": {"type": "long"},
    # nginx 请求主机
    "x_http_host": {"type": "keyword"},
    # nginx 请求来源
    "x_http_referer": {"type": "text", "index": False},
    # nginx 用户代理
    "x_http_user_agent": {"type": "text", "index": False},
    # nginx 反代来源
    "x_http_x_forwarded_for": {"type": "keyword", "index": False},
    # nginx http 协议
    "x_protocol": {"type": "keyword"},
    # nginx 远程地址
    "x_remote_addr": {"type": "keyword"},
    # 请求用时
    "x_request_time": {"type": "long"},
    # 反代后端地址
    "x_upstream_addr": {"type": "keyword"},
    # 后端响应时间
    "x_upstream_response_time": {"type": "long"},
    # 相应大小
    "x_response_size": {"type":"long"},
    # 通用整数值
    "x_value_integer": {"type": "long"},
    # redis 操作
    "x_cmd": {"type": "keyword"},
    # redis 操作摘要
    "x_cmd_digest": {"type": "keyword"},
    # redis 操作键值
    "x_key": {"type": "keyword"},
    # redis 操作参数
    "x_param_value": {"type": "text", "index": False},
    # redis 参数大小
    "x_param_value_size": {"type": "long"},
    # logtube 版本号
    "x_logtube_version": {"type":"keyword"},
    # 生命周期类型（boot, logtube-reload)
    "x_lifecycle": {"type": "keyword"}
}

MESSAGE_WITH_INDEX = {
    # 消息（带索引）
    "message": {
        "type": "text"
    }
}


def build_template(name: str, patterns: List[str], *fieldsSet: Dict):
    # 组合多组 fields
    properties = {}
    for fields in fieldsSet:
        for key in fields:
            properties[key] = fields[key]

    # 构造模板描述
    data = {
        "index_patterns": patterns,
        "settings": {
            "index": {
                "codec": "best_compression",
                "routing": {"allocation": {"exclude": {"disktype": "hdd"}}},
                "refresh_interval": "10s",
                "number_of_shards": "6",
                "translog": {"sync_interval": "10s", "durability": "async"},
                "number_of_replicas": "0"
            }
        },
        "mappings": {"_doc": {"properties": properties}},
        "aliases": {}
    }
    # 写入模板描述文件
    with open(os.path.join("templates", name+'.json'), 'w') as out:
        json.dump(data, out,  indent=2, separators=(',', ': '))

    # 构造没有 _doc 的模板描述
    data = {
        "index_patterns": patterns,
        "settings": {
            "index": {
                "codec": "best_compression",
                "routing": {"allocation": {"exclude": {"disktype": "hdd"}}},
                "refresh_interval": "10s",
                "number_of_shards": "6",
                "translog": {"sync_interval": "10s", "durability": "async"},
                "number_of_replicas": "0"
            }
        },
        "mappings": {"properties": properties},
        "aliases": {}
    }
    # 写入模板描述文件
    with open(os.path.join("templates-nomt", name+'.json'), 'w') as out:
        json.dump(data, out,  indent=2, separators=(',', ': '))

    # 构造没有 _doc 的模板 且分片数为 3 的模板
    data = {
        "index_patterns": patterns,
        "settings": {
            "index": {
                "codec": "best_compression",
                "routing": {"allocation": {"exclude": {"disktype": "hdd"}}},
                "refresh_interval": "10s",
                "number_of_shards": "3",
                "translog": {"sync_interval": "10s", "durability": "async"},
                "number_of_replicas": "0"
            }
        },
        "mappings": {"properties": properties},
        "aliases": {}
    }
    # 写入模板描述文件
    with open(os.path.join("templates-nomt-shim", name+'.json'), 'w') as out:
        json.dump(data, out,  indent=2, separators=(',', ': '))

build_template("x-access", ["x-access-*"], COMMON)
build_template("x-audit", ["x-audit-*"], COMMON)
build_template("x-druid-track", ["x-druid-track-*"], COMMON)
build_template("x-err", ["err-*", "error-*"], COMMON, MESSAGE_WITH_INDEX)
build_template("x-fatal", ["fatal-*"], COMMON, MESSAGE_WITH_INDEX)
build_template("x-http-invoke", ["http-invoke-*"], COMMON)
build_template("x-info", ["info-*"], COMMON)
build_template("x-mybatis-track", ["x-mybatis-track-*"], COMMON)
build_template("x-mysql-error", ["x-mysql-error-*"], COMMON)
build_template("x-nginx-access", ["x-nginx-access-*"], COMMON)
build_template("x-perf", ["x-perf-*"], COMMON)
build_template("x-redis-track", ["x-redis-track-*"], COMMON)
build_template("x-warn", ["warn-*"], COMMON)
build_template("x-debug", ["debug-*"], COMMON)
build_template("x-lifecycle", ["lifecycle-*"], COMMON)
build_template("x-sql", ["sql-*"], COMMON)
