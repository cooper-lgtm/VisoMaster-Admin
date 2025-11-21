import { LogoutOutlined } from "@ant-design/icons";
import { Button, Layout, Menu, Space, Typography } from "antd";
import { useMemo } from "react";
import { Link, Outlet, useLocation, useNavigate } from "react-router-dom";
import { authStore } from "../store/auth";

const { Header, Content, Sider } = Layout;

const DashboardLayout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const logout = authStore((s) => s.logout);

  const selectedKeys = useMemo(() => {
    if (location.pathname.startsWith("/users")) return ["users"];
    if (location.pathname.startsWith("/images")) return ["images"];
    if (location.pathname.startsWith("/assignments")) return ["assignments"];
    return ["dashboard"];
  }, [location.pathname]);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider width={220} theme="light" style={{ borderRight: "1px solid #f0f0f0" }}>
        <div style={{ padding: "16px 24px", fontWeight: 700, fontSize: 20, color: "var(--text)" }}>VisoMaster</div>
        <Menu
          mode="inline"
          selectedKeys={selectedKeys}
          items={[
            { key: "dashboard", label: <Link to="/">仪表盘</Link> },
            { key: "users", label: <Link to="/users">用户管理</Link> },
            { key: "images", label: <Link to="/images">图片库</Link> },
            { key: "assignments", label: <Link to="/assignments">分配</Link> },
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ background: "#fff", padding: "0 24px", borderBottom: "1px solid #f0f0f0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <Typography.Text style={{ fontSize: 16, fontWeight: 600 }}>后台管理</Typography.Text>
          <Space>
            <Button icon={<LogoutOutlined />} onClick={() => { logout(); navigate("/login"); }}>
              退出
            </Button>
          </Space>
        </Header>
        <Content style={{ padding: 24 }}>
          <div style={{ minHeight: "calc(100vh - 120px)" }}>
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default DashboardLayout;
