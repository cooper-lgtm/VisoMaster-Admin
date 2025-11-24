import { UploadOutlined } from "@ant-design/icons";
import { Upload, message } from "antd";
import axios from "axios";
import type { RcFile, UploadRequestOption } from "rc-upload/lib/interface";
import { requestUploadUrl, saveImageMetadata } from "../api/images";

type Props = {
  onUploaded: () => void;
};

const ImageUpload = ({ onUploaded }: Props) => {
  const handleUpload = async (options: UploadRequestOption<any>) => {
    const file = options.file as RcFile;
    try {
      const presigned = await requestUploadUrl({ filename: file.name, content_type: file.type });
      await axios.put(presigned.url, file, { headers: { "Content-Type": file.type || "application/octet-stream" } });
      await saveImageMetadata({
        bucket: presigned.bucket,
        key: presigned.key,
        filename: file.name,
        mime_type: file.type,
        size_bytes: file.size,
      });
      message.success("上传成功");
      onUploaded();
      options.onSuccess && options.onSuccess({}, new XMLHttpRequest());
    } catch (error: any) {
      message.error(error.response?.data?.detail || "上传失败");
      options.onError && options.onError(error);
    }
  };

  return (
    <Upload customRequest={handleUpload} showUploadList={false} accept="image/*" multiple>
      <div
        style={{
          padding: "12px 16px",
          border: "1px dashed #1677ff",
          borderRadius: 8,
          color: "#1677ff",
          cursor: "pointer",
          display: "inline-flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        <UploadOutlined /> 上传图片
      </div>
    </Upload>
  );
};

export default ImageUpload;
