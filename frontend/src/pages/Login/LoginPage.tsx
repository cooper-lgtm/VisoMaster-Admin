import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Checkbox, Form, Input, Typography, message } from "antd";
import { useNavigate } from "react-router-dom";
import { adminLogin } from "../../api/auth";
import { authStore } from "../../store/auth";

const LoginPage = () => {
  const navigate = useNavigate();
  const setToken = authStore((s) => s.setToken);

  const onFinish = async (values: { username: string; password: string }) => {
    try {
      const res = await adminLogin(values);
      setToken(res.access_token, { username: values.username });
      navigate("/");
    } catch (error: any) {
      message.error(error.response?.data?.detail || "登录失败");
    }
  };

  return (
    <div>
      <Typography.Title level={3} style={{ marginBottom: 4 }}>
        管理后台登录
      </Typography.Title>
      <Typography.Text type="secondary">使用管理员账号进入后台</Typography.Text>
      <Form layout="vertical" style={{ marginTop: 32 }} initialValues={{ remember: true }} onFinish={onFinish}>
        <Form.Item name="username" rules={[{ required: true, message: "请输入账号" }]}>
          <Input prefix={<UserOutlined />} size="large" placeholder="管理员账号" autoComplete="username" />
        </Form.Item>
        <Form.Item name="password" rules={[{ required: true, message: "请输入密码" }]}>
          <Input.Password
            prefix={<LockOutlined />}
            size="large"
            placeholder="密码"
            autoComplete="current-password"
          />
        </Form.Item>
        <Form.Item name="remember" valuePropName="checked" noStyle>
          <Checkbox>记住我</Checkbox>
        </Form.Item>
        <Form.Item style={{ marginTop: 24 }}>
          <Button type="primary" htmlType="submit" block size="large">
            登录
          </Button>
        </Form.Item>
      </Form>
    </div>
  );
};

export default LoginPage;
