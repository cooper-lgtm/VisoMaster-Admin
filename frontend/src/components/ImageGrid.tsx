import { DeleteOutlined, LinkOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Card, Col, Image as AntImage, Row, Space, Tag, Tooltip } from "antd";
import type { Image } from "../api/images";

type Props = {
  data: Image[];
  onDelete: (img: Image) => void;
};

const ImageGrid = ({ data, onDelete }: Props) => {
  return (
    <Row gutter={[16, 16]}>
      {data.map((img) => (
        <Col xs={24} sm={12} md={8} lg={6} key={img.id}>
          <Card
            hoverable
            cover={
              img.presigned_url ? (
                <AntImage
                  src={img.presigned_url}
                  alt={img.filename}
                  style={{ height: 180, objectFit: "cover" }}
                  preview={false}
                />
              ) : null
            }
            actions={[
              <Tooltip key="open" title="预览链接">
                <a href={img.presigned_url} target="_blank" rel="noreferrer">
                  <LinkOutlined />
                </a>
              </Tooltip>,
              <Tooltip key="delete" title="删除">
                <Button type="text" danger icon={<DeleteOutlined />} onClick={() => onDelete(img)} />
              </Tooltip>,
            ]}
          >
            <Card.Meta
              title={img.filename}
              description={
                <Space direction="vertical">
                  <span>
                    <Tag color="blue">{img.mime_type || "image"}</Tag>
                    <Tag icon={<UserOutlined />}>{img.uploader_admin_id || "—"}</Tag>
                  </span>
                  <small>{img.key}</small>
                </Space>
              }
            />
          </Card>
        </Col>
      ))}
    </Row>
  );
};

export default ImageGrid;
