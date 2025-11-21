import { EditOutlined, KeyOutlined, StopOutlined, SyncOutlined } from "@ant-design/icons";
import { Button, Popconfirm, Space, Table, Tag, Tooltip } from "antd";
import dayjs from "dayjs";
import type { User } from "../api/users";

type Props = {
  data: User[];
  loading?: boolean;
  onEdit: (user: User) => void;
  onExtend: (user: User) => void;
  onResetPassword: (user: User) => void;
  onToggleStatus: (user: User) => void;
};

const UserTable = ({ data, loading, onEdit, onExtend, onResetPassword, onToggleStatus }: Props) => {
  return (
    <Table
      dataSource={data}
      loading={loading}
      rowKey="id"
      pagination={{ pageSize: 10, showSizeChanger: false }}
      columns={[
        { title: "账号", dataIndex: "username" },
        {
          title: "状态",
          dataIndex: "status",
          render: (value) => <Tag color={value === "active" ? "green" : "red"}>{value}</Tag>,
        },
        {
          title: "到期时间",
          dataIndex: "expires_at",
          render: (value) => (value ? dayjs(value).format("YYYY-MM-DD HH:mm") : "—"),
        },
        {
          title: "创建时间",
          dataIndex: "created_at",
          render: (value) => dayjs(value).format("YYYY-MM-DD"),
        },
        {
          title: "操作",
          render: (_, record) => (
            <Space>
              <Tooltip title="编辑">
                <Button icon={<EditOutlined />} size="small" onClick={() => onEdit(record)} />
              </Tooltip>
              <Tooltip title="延期">
                <Button icon={<SyncOutlined />} size="small" onClick={() => onExtend(record)} />
              </Tooltip>
              <Tooltip title="重置密码">
                <Button icon={<KeyOutlined />} size="small" onClick={() => onResetPassword(record)} />
              </Tooltip>
              <Popconfirm
                title={record.status === "active" ? "禁用该用户？" : "启用该用户？"}
                onConfirm={() => onToggleStatus(record)}
              >
                <Button icon={<StopOutlined />} size="small" danger={record.status === "active"} />
              </Popconfirm>
            </Space>
          ),
        },
      ]}
    />
  );
};

export default UserTable;
