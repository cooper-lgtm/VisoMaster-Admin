import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Card, Modal, Skeleton, message } from "antd";
import { deleteImage, fetchImages, type Image } from "../../api/images";
import ImageGrid from "../../components/ImageGrid";
import ImageUpload from "../../components/ImageUpload";

const ImagesPage = () => {
  const queryClient = useQueryClient();
  const { data: images = [], isLoading } = useQuery({ queryKey: ["images"], queryFn: fetchImages });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteImage(id),
    onSuccess: () => {
      message.success("已删除");
      queryClient.invalidateQueries({ queryKey: ["images"] });
    },
  });

  const handleDelete = (img: Image) => {
    Modal.confirm({
      title: `删除 ${img.filename}?`,
      onOk: async () => {
        try {
          await deleteMutation.mutateAsync(img.id);
        } catch (error: any) {
          message.error(error.response?.data?.detail || "删除失败");
        }
      },
    });
  };

  return (
    <Card
      title="图片库"
      extra={<ImageUpload onUploaded={() => queryClient.invalidateQueries({ queryKey: ["images"] })} />}
    >
      {isLoading ? <Skeleton active /> : <ImageGrid data={images} onDelete={handleDelete} />}
    </Card>
  );
};

export default ImagesPage;
