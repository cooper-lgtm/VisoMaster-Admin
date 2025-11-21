import { useQuery } from "@tanstack/react-query";
import { Card, Col, Row, Skeleton, Statistic } from "antd";
import { fetchStats } from "../../api/stats";

const DashboardPage = () => {
  const { data, isLoading } = useQuery({ queryKey: ["stats"], queryFn: fetchStats });

  const cards = [
    { title: "用户总数", field: "total_users" },
    { title: "启用用户", field: "active_users" },
    { title: "禁用用户", field: "disabled_users" },
    { title: "即将到期", field: "expiring_users" },
    { title: "图片数量", field: "total_images" },
  ] as const;

  return (
    <Row gutter={[16, 16]}>
      {cards.map((c) => (
        <Col xs={24} sm={12} md={8} lg={6} key={c.field}>
          <Card>
            {isLoading || !data ? (
              <Skeleton active paragraph={false} />
            ) : (
              <Statistic title={c.title} value={data[c.field]} />
            )}
          </Card>
        </Col>
      ))}
    </Row>
  );
};

export default DashboardPage;
