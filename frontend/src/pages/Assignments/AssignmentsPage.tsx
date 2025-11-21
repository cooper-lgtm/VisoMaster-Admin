import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Col, DatePicker, Form, Row, Select, Space, message } from "antd";
import dayjs from "dayjs";
import { assignImagesToUser, assignUsersToImage } from "../../api/assignments";
import { fetchImages, type Image } from "../../api/images";
import { fetchUsers, type User } from "../../api/users";

const AssignmentsPage = () => {
  const queryClient = useQueryClient();
  const { data: users = [] } = useQuery({ queryKey: ["users"], queryFn: fetchUsers });
  const { data: images = [] } = useQuery({ queryKey: ["images"], queryFn: fetchImages });

  const assignImgMutation = useMutation({
    mutationFn: ({ userId, imageIds, expires_at }: { userId: number; imageIds: number[]; expires_at?: string }) =>
      assignImagesToUser(userId, imageIds, expires_at),
    onSuccess: () => {
      message.success("分配成功");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const assignUserMutation = useMutation({
    mutationFn: ({ imageId, userIds, expires_at }: { imageId: number; userIds: number[]; expires_at?: string }) =>
      assignUsersToImage(imageId, userIds, expires_at),
    onSuccess: () => {
      message.success("分配成功");
      queryClient.invalidateQueries({ queryKey: ["images"] });
    },
  });

  return (
    <Row gutter={16}>
      <Col xs={24} md={12}>
        <Card title="给用户分配图片">
          <Form
            layout="vertical"
            onFinish={async (values) => {
              await assignImgMutation.mutateAsync({
                userId: values.user_id,
                imageIds: values.image_ids,
                expires_at: values.expires_at ? values.expires_at.toDate().toISOString() : undefined,
              });
            }}
          >
            <Form.Item name="user_id" label="选择用户" rules={[{ required: true }]}>
              <Select
                placeholder="选择用户"
                options={users.map((u: User) => ({ label: u.username, value: u.id }))}
                showSearch
                optionFilterProp="label"
              />
            </Form.Item>
            <Form.Item name="image_ids" label="选择图片" rules={[{ required: true }]}>
              <Select
                mode="multiple"
                placeholder="选择图片"
                options={images.map((img: Image) => ({ label: img.filename, value: img.id }))}
                showSearch
                optionFilterProp="label"
              />
            </Form.Item>
            <Form.Item name="expires_at" label="到期时间">
              <DatePicker showTime style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={assignImgMutation.isPending}>
                分配
              </Button>
            </Form.Item>
          </Form>
        </Card>
      </Col>
      <Col xs={24} md={12}>
        <Card title="给图片分配用户">
          <Form
            layout="vertical"
            onFinish={async (values) => {
              await assignUserMutation.mutateAsync({
                imageId: values.image_id,
                userIds: values.user_ids,
                expires_at: values.expires_at ? values.expires_at.toDate().toISOString() : undefined,
              });
            }}
          >
            <Form.Item name="image_id" label="选择图片" rules={[{ required: true }]}>
              <Select
                placeholder="选择图片"
                options={images.map((img: Image) => ({ label: img.filename, value: img.id }))}
                showSearch
                optionFilterProp="label"
              />
            </Form.Item>
            <Form.Item name="user_ids" label="选择用户" rules={[{ required: true }]}>
              <Select
                mode="multiple"
                placeholder="选择用户"
                options={users.map((u: User) => ({ label: u.username, value: u.id }))}
                showSearch
                optionFilterProp="label"
              />
            </Form.Item>
            <Form.Item name="expires_at" label="到期时间">
              <DatePicker showTime style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit" loading={assignUserMutation.isPending}>
                  分配
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      </Col>
    </Row>
  );
};

export default AssignmentsPage;
