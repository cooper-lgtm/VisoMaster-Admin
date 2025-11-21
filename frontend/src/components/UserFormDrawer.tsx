import { Drawer, Form, Input, DatePicker, Select, Space, Button } from "antd";
import dayjs from "dayjs";
import { useEffect } from "react";
import type { CreateUserDto, UpdateUserDto, User } from "../api/users";

type Props = {
  open: boolean;
  onClose: () => void;
  onSubmit: (values: CreateUserDto | UpdateUserDto) => Promise<void>;
  editing?: User | null;
};

const statusOptions = [
  { value: "active", label: "启用" },
  { value: "disabled", label: "禁用" },
];

const UserFormDrawer = ({ open, onClose, onSubmit, editing }: Props) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (editing) {
      form.setFieldsValue({
        username: editing.username,
        status: editing.status,
        expires_at: editing.expires_at ? dayjs(editing.expires_at) : null,
        notes: editing.notes,
      });
    } else {
      form.resetFields();
    }
  }, [editing, form]);

  const handleFinish = async (values: any) => {
    const payload: any = {
      ...values,
      expires_at: values.expires_at ? values.expires_at.toDate().toISOString() : null,
    };
    await onSubmit(payload);
    form.resetFields();
  };

  return (
    <Drawer
      title={editing ? "编辑用户" : "创建用户"}
      width={420}
      onClose={onClose}
      open={open}
      destroyOnClose
      extra={
        <Space>
          <Button onClick={onClose}>取消</Button>
          <Button type="primary" onClick={() => form.submit()}>
            保存
          </Button>
        </Space>
      }
    >
      <Form layout="vertical" form={form} onFinish={handleFinish}>
        <Form.Item name="username" label="账号" rules={[{ required: true, message: "请输入账号" }]}>
          <Input disabled={!!editing} />
        </Form.Item>
        <Form.Item
          name="password"
          label="密码"
          rules={editing ? [] : [{ required: true, message: "请输入密码" }]}
          help={editing ? "留空则不修改密码" : undefined}
        >
          <Input.Password />
        </Form.Item>
        <Form.Item name="status" label="状态" initialValue="active">
          <Select options={statusOptions} />
        </Form.Item>
        <Form.Item name="expires_at" label="到期时间">
          <DatePicker showTime style={{ width: "100%" }} />
        </Form.Item>
        <Form.Item name="notes" label="备注">
          <Input.TextArea rows={3} />
        </Form.Item>
      </Form>
    </Drawer>
  );
};

export default UserFormDrawer;
