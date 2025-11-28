import { CheckCircleFilled, EyeOutlined } from "@ant-design/icons";
import { Card, Checkbox, Col, Image as AntImage, Row } from "antd";
import type { Image } from "../api/images";

type Props = {
  data: Image[];
  selectedIds: number[];
  onToggleSelect: (img: Image) => void;
  onPreview: (img: Image) => void;
};

const ImageGrid = ({ data, selectedIds, onToggleSelect, onPreview }: Props) => {
  return (
    <Row gutter={[16, 16]}>
      {data.map((img) => {
        const selected = selectedIds.includes(img.id);
        const coverSrc = img.thumb_url || img.download_url || img.presigned_url;
        const previewSrc = img.download_url || img.presigned_url;
        return (
          <Col xs={24} sm={12} md={8} lg={6} key={img.id}>
            <Card
              hoverable
              style={selected ? { borderColor: "#1677ff", boxShadow: "0 0 0 2px rgba(22,119,255,0.2)" } : {}}
              onClick={() => onToggleSelect(img)}
              cover={
                <div style={{ position: "relative" }}>
                  {coverSrc ? (
                    <AntImage
                      src={coverSrc}
                      alt={img.filename}
                      style={{ height: 200, objectFit: "cover", borderTopLeftRadius: 8, borderTopRightRadius: 8 }}
                      preview={false}
                    />
                  ) : null}
                  <Checkbox
                    checked={selected}
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleSelect(img);
                    }}
                    style={{
                      position: "absolute",
                      top: 8,
                      left: 8,
                      background: "rgba(255,255,255,0.9)",
                      borderRadius: 12,
                      padding: "2px 4px",
                    }}
                  />
                  {previewSrc ? (
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        onPreview(img);
                      }}
                      style={{
                        position: "absolute",
                        top: 8,
                        right: 8,
                        background: "rgba(0,0,0,0.55)",
                        color: "#fff",
                        borderRadius: "50%",
                        width: 28,
                        height: 28,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        cursor: "pointer",
                      }}
                    >
                      <EyeOutlined />
                    </div>
                  ) : null}
                  {selected && (
                    <CheckCircleFilled
                      style={{
                        position: "absolute",
                        bottom: 8,
                        right: 8,
                        color: "#1677ff",
                        fontSize: 22,
                        textShadow: "0 1px 4px rgba(0,0,0,0.3)",
                      }}
                    />
                  )}
                </div>
              }
            >
              <Card.Meta title={img.filename} />
            </Card>
          </Col>
        );
      })}
    </Row>
  );
};

export default ImageGrid;
