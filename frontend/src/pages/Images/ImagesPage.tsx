import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Form, Image as AntImage, Modal, Select, Skeleton, Space, message } from "antd";
import { useMemo, useState } from "react";
import { assignImagesToUser } from "../../api/assignments";
import { deleteImage, fetchImages, type Image } from "../../api/images";
import { fetchUsers, type User } from "../../api/users";
import ImageGrid from "../../components/ImageGrid";
import ImageUpload from "../../components/ImageUpload";

const ImagesPage = () => {
  const queryClient = useQueryClient();
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [assignOpen, setAssignOpen] = useState(false);
  const [previewImg, setPreviewImg] = useState<Image | null>(null);
  const [form] = Form.useForm();

  const { data: images = [], isLoading } = useQuery({ queryKey: ["images"], queryFn: fetchImages });
  const { data: users = [] } = useQuery({ queryKey: ["users"], queryFn: fetchUsers });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteImage(id),
    onSuccess: () => {
      message.success("已删除");
      queryClient.invalidateQueries({ queryKey: ["images"] });
    },
  });

  const assignMutation = useMutation({
    mutationFn: ({ userId, imageIds }: { userId: number; imageIds: number[] }) =>
      assignImagesToUser(userId, imageIds),
    onSuccess: () => {
      message.success("分配成功");
      setAssignOpen(false);
      setSelectedIds([]);
      queryClient.invalidateQueries({ queryKey: ["images"] });
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const handleDeleteSingle = (img: Image) => {
    Modal.confirm({
      title: `删除 ${img.filename}?`,
      onOk: async () => {
        try {
          await deleteMutation.mutateAsync(img.id);
          setSelectedIds((prev) => prev.filter((id) => id !== img.id));
        } catch (error: any) {
          message.error(error.response?.data?.detail || "删除失败");
        }
      },
    });
  };

  const handleBulkDelete = () => {
    if (!selectedIds.length) {
      message.info("请先选择图片");
      return;
    }
    Modal.confirm({
      title: `删除选中的 ${selectedIds.length} 张图片？`,
      onOk: async () => {
        const results = await Promise.allSettled(selectedIds.map((id) => deleteImage(id)));
        const okCount = results.filter((r) => r.status === "fulfilled").length;
        if (okCount) {
          message.success(`已删除 ${okCount} 张图片`);
          queryClient.invalidateQueries({ queryKey: ["images"] });
        }
        setSelectedIds([]);
      },
    });
  };

  const handleAssign = () => {
    if (!selectedIds.length) {
      message.info("请先选择图片");
      return;
    }
    setAssignOpen(true);
  };

  const handleToggleSelect = (img: Image) => {
    setSelectedIds((prev) => (prev.includes(img.id) ? prev.filter((id) => id !== img.id) : [...prev, img.id]));
  };

  const userOptions = useMemo(
    () => users.map((u: User) => ({ label: u.username, value: u.id })),
    [users],
  );

  return (
    <>
      <Card
        title="图片库"
        extra={
          <Space>
            <ImageUpload onUploaded={() => queryClient.invalidateQueries({ queryKey: ["images"] })} />
            <Button onClick={handleAssign} disabled={!selectedIds.length}>
              分配
            </Button>
            <Button danger onClick={handleBulkDelete} disabled={!selectedIds.length} loading={deleteMutation.isPending}>
              删除
            </Button>
          </Space>
        }
      >
        {isLoading ? (
          <Skeleton active />
        ) : (
          <ImageGrid
            data={images}
            selectedIds={selectedIds}
            onToggleSelect={handleToggleSelect}
            onPreview={(img) => setPreviewImg(img)}
          />
        )}
      </Card>

      <Modal
        title={`分配图片 (${selectedIds.length})`}
        open={assignOpen}
        onCancel={() => setAssignOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={assignMutation.isPending}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={async (values) => {
            try {
              await assignMutation.mutateAsync({ userId: values.user_id, imageIds: selectedIds });
            } catch (error: any) {
              message.error(error.response?.data?.detail || "分配失败");
            }
          }}
        >
          <Form.Item name="user_id" label="选择用户" rules={[{ required: true, message: "请选择用户" }]}>
            <Select
              options={userOptions}
              placeholder="选择用户"
              showSearch
              optionFilterProp="label"
            />
          </Form.Item>
        </Form>
      </Modal>

      <Modal open={!!previewImg} onCancel={() => setPreviewImg(null)} footer={null} width={900} centered>
        {previewImg && (
          <>
            <AntImage src={previewImg.presigned_url} alt={previewImg.filename} style={{ width: "100%" }} />
            <div style={{ marginTop: 8, fontWeight: 600 }}>{previewImg.filename}</div>
          </>
        )}
      </Modal>
    </>
  );
};

export default ImagesPage;
