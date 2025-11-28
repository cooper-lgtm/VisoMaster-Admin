import { UploadOutlined } from "@ant-design/icons";
import { Upload, message } from "antd";
import type { RcFile, UploadRequestOption } from "rc-upload/lib/interface";
import { apiClient } from "../api/client";

type Props = {
  onUploaded: () => void;
};

const ImageUpload = ({ onUploaded }: Props) => {
  const handleUpload = async (options: UploadRequestOption<any>) => {
    const file = options.file as RcFile;
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await apiClient.post("/images/upload-file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      message.success("上传成功");
      onUploaded();
      options.onSuccess && options.onSuccess(data, new XMLHttpRequest());
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
