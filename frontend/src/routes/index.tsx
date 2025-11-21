import { ReactNode } from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";
import AuthLayout from "../layouts/AuthLayout";
import DashboardLayout from "../layouts/DashboardLayout";
import AssignmentsPage from "../pages/Assignments/AssignmentsPage";
import DashboardPage from "../pages/Dashboard/DashboardPage";
import ImagesPage from "../pages/Images/ImagesPage";
import LoginPage from "../pages/Login/LoginPage";
import UsersPage from "../pages/Users/UsersPage";
import { authStore } from "../store/auth";

const RequireAuth = ({ children }: { children: ReactNode }) => {
  const token = authStore((s) => s.token);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

export const router = createBrowserRouter([
  {
    path: "/login",
    element: (
      <AuthLayout>
        <LoginPage />
      </AuthLayout>
    ),
  },
  {
    path: "/",
    element: (
      <RequireAuth>
        <DashboardLayout />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "users", element: <UsersPage /> },
      { path: "images", element: <ImagesPage /> },
      { path: "assignments", element: <AssignmentsPage /> },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);
