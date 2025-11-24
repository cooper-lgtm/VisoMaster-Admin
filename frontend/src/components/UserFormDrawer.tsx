import { Drawer, Form, Input, DatePicker, Select, Space, Button, Tag, Typography, Modal, message, Image as AntImage } from "antd";
import dayjs from "dayjs";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { CreateUserDto, UpdateUserDto, User } from "../api/users";
import { fetchImagesForUser, unassignImageFromUser } from "../api/assignments";
import type { Image } from "../api/images";

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
  const queryClient = useQueryClient();
  const [previewImg, setPreviewImg] = useState<Image | null>(null);

  const { data: assignedImages = [], isFetching: loadingAssigned } = useQuery({
    queryKey: ["user-images", editing?.id],
    queryFn: () => fetchImagesForUser(editing!.id),
    enabled: !!editing,
  });

  const unassignMutation = useMutation({
    mutationFn: ({ userId, imageId }: { userId: number; imageId: number }) => unassignImageFromUser(userId, imageId),
    onSuccess: () => {
      message.success("已移除分配");
      queryClient.invalidateQueries({ queryKey: ["user-images", editing?.id] });
    },
  });

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

  const handleRemoveAssign = (img: Image) => {
    if (!editing) return;
    Modal.confirm({
      title: `移除分配：${img.filename}?`,
      onOk: async () => {
        try {
          await unassignMutation.mutateAsync({ userId: editing.id, imageId: img.id });
        } catch (error: any) {
          message.error(error.response?.data?.detail || "移除失败");
        }
      },
    });
  };

  const assignedContent = useMemo(() => {
    if (!editing) return null;
    if (loadingAssigned) return <Typography.Text type="secondary">加载中…</Typography.Text>;
    if (!assignedImages.length) return <Typography.Text type="secondary">尚未分配图片</Typography.Text>;
    return (
      <Space size={[8, 8]} wrap>
        {assignedImages.map((img) => (
          <Tag
            key={img.id}
            closable
            onClose={(e) => {
              e.preventDefault();
              handleRemoveAssign(img);
            }}
            onClick={() => setPreviewImg(img)}
            style={{ cursor: "pointer", marginBottom: 0 }}
          >
            {img.filename}
          </Tag>
        ))}
      </Space>
    );
  }, [assignedImages, editing, loadingAssigned]);

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
        {editing ? (
          <Form.Item label="已分配图片" colon={false}>
            {assignedContent}
          </Form.Item>
        ) : null}
        <Form.Item name="notes" label="备注">
          <Input.TextArea rows={3} />
        </Form.Item>
      </Form>
      <Modal open={!!previewImg} footer={null} onCancel={() => setPreviewImg(null)} width={900} centered>
        {previewImg && (
          <>
            <AntImage src={previewImg.presigned_url} alt={previewImg.filename} style={{ width: "100%" }} />
            <div style={{ marginTop: 8, fontWeight: 600 }}>{previewImg.filename}</div>
          </>
        )}
      </Modal>
    </Drawer>
  );
};

export default UserFormDrawer;
