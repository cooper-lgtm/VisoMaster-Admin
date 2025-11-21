import { Modal, DatePicker, Form, Input } from "antd";
import dayjs from "dayjs";
import { useEffect } from "react";
import type { User } from "../api/users";

type Props = {
  open: boolean;
  onOk: (date: string, reason?: string) => Promise<void>;
  onCancel: () => void;
  user?: User | null;
};

const ExtendModal = ({ open, onOk, onCancel, user }: Props) => {
  const [form] = Form.useForm();
  useEffect(() => {
    form.setFieldsValue({ expires_at: user?.expires_at ? dayjs(user.expires_at) : null, reason: undefined });
  }, [user, form]);
  return (
    <Modal
      title={`延期用户 ${user?.username || ""}`}
      open={open}
      okText="确认延期"
      cancelText="取消"
      onCancel={() => {
        form.resetFields();
        onCancel();
      }}
      onOk={() => form.submit()}
    >
      <Form
        layout="vertical"
        form={form}
        initialValues={{ expires_at: user?.expires_at ? dayjs(user.expires_at) : null }}
        onFinish={(values) => onOk(values.expires_at.toDate().toISOString(), values.reason)}
      >
        <Form.Item name="expires_at" label="新的到期时间" rules={[{ required: true, message: "请选择时间" }]}>
          <DatePicker showTime style={{ width: "100%" }} />
        </Form.Item>
        <Form.Item name="reason" label="原因">
          <Input.TextArea rows={3} />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ExtendModal;
