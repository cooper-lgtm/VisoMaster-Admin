import { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

const AuthLayout = ({ children }: Props) => {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <div className="login-hero" style={{ flex: 1, padding: "64px 48px" }}>
        <div style={{ maxWidth: 420, margin: "0 auto" }}>
          <h1 style={{ marginBottom: 12, fontSize: 36 }}>VisoMaster Admin</h1>
          <p style={{ lineHeight: 1.8, fontSize: 16, color: "rgba(255,255,255,0.9)" }}>
            管理用户、图片与分配，一站式后台。账号到期、延期、禁用与图片授权都可以在仪表盘中快速完成。
          </p>
        </div>
      </div>
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: 420, padding: "48px 56px", background: "#fff", borderRadius: 16, boxShadow: "0 30px 80px rgba(0,0,0,0.08)" }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
