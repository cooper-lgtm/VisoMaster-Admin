import { PlusOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Card, Input, Modal, Space, message } from "antd";
import { useMemo, useState } from "react";
import ExtendModal from "../../components/ExtendModal";
import UserFormDrawer from "../../components/UserFormDrawer";
import UserTable from "../../components/UserTable";
import {
  createUser,
  extendUser,
  fetchUsers,
  resetPassword,
  updateUser,
  type User,
  type CreateUserDto,
  type UpdateUserDto,
} from "../../api/users";

const UsersPage = () => {
  const queryClient = useQueryClient();
  const { data: users = [], isLoading } = useQuery({ queryKey: ["users"], queryFn: fetchUsers });
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [extendTarget, setExtendTarget] = useState<User | null>(null);
  const [resetTarget, setResetTarget] = useState<User | null>(null);
  const [password, setPassword] = useState("");

  const createMutation = useMutation({
    mutationFn: (payload: CreateUserDto) => createUser(payload),
    onSuccess: () => {
      message.success("创建成功");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: UpdateUserDto }) => updateUser(id, payload),
    onSuccess: () => {
      message.success("更新成功");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const extendMutation = useMutation({
    mutationFn: ({ id, date, reason }: { id: number; date: string; reason?: string }) =>
      extendUser(id, date, reason),
    onSuccess: () => {
      message.success("已延期");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const resetMutation = useMutation({
    mutationFn: ({ id, password }: { id: number; password: string }) => resetPassword(id, password),
    onSuccess: () => {
      message.success("密码已重置");
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const handleSubmit = async (payload: CreateUserDto | UpdateUserDto) => {
    try {
      if (editing) {
        await updateMutation.mutateAsync({ id: editing.id, payload });
      } else {
        await createMutation.mutateAsync(payload as CreateUserDto);
      }
      setDrawerOpen(false);
      setEditing(null);
    } catch (error: any) {
      message.error(error.response?.data?.detail || "操作失败");
    }
  };

  const handleExtend = async (date: string, reason?: string) => {
    if (!extendTarget) return;
    try {
      await extendMutation.mutateAsync({ id: extendTarget.id, date, reason });
    } catch (error: any) {
      message.error(error.response?.data?.detail || "延期失败");
    } finally {
      setExtendTarget(null);
    }
  };

  const handleReset = async () => {
    if (!resetTarget) return;
    if (!password) {
      message.warning("请输入新密码");
      return;
    }
    try {
      await resetMutation.mutateAsync({ id: resetTarget.id, password });
      setResetTarget(null);
      setPassword("");
    } catch (error: any) {
      message.error(error.response?.data?.detail || "重置失败");
    }
  };

  const handleStatusToggle = async (user: User) => {
    const newStatus = user.status === "active" ? "disabled" : "active";
    try {
      await updateMutation.mutateAsync({ id: user.id, payload: { status: newStatus } });
    } catch (error: any) {
      message.error("操作失败");
    }
  };

  const header = useMemo(
    () => (
      <Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setDrawerOpen(true)}>
          新建用户
        </Button>
      </Space>
    ),
    [],
  );

  return (
    <Card title="用户管理" extra={header}>
      <UserTable
        data={users}
        loading={isLoading}
        onEdit={(u) => {
          setEditing(u);
          setDrawerOpen(true);
        }}
        onExtend={(u) => setExtendTarget(u)}
        onResetPassword={(u) => setResetTarget(u)}
        onToggleStatus={handleStatusToggle}
      />

      <UserFormDrawer
        open={drawerOpen}
        editing={editing}
        onClose={() => {
          setDrawerOpen(false);
          setEditing(null);
        }}
        onSubmit={handleSubmit}
      />

      <ExtendModal open={!!extendTarget} user={extendTarget} onCancel={() => setExtendTarget(null)} onOk={handleExtend} />

      <Modal
        title={`重置 ${resetTarget?.username} 密码`}
        open={!!resetTarget}
        onCancel={() => {
          setResetTarget(null);
          setPassword("");
        }}
        okText="重置"
        onOk={handleReset}
      >
        <Input.Password value={password} onChange={(e) => setPassword(e.target.value)} placeholder="新密码" />
      </Modal>
    </Card>
  );
};

export default UsersPage;
