import { Avatar, Dropdown, MenuProps } from "antd"
import { LogoutOutlined, ProfileOutlined, StarOutlined, UserOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useLogout } from "../../hooks/use-logout";



const UserMenu = () => {
  const navigate = useNavigate();
  const { logout } = useLogout();

  const items: MenuProps['items'] = [
    {
      key: 'my-cv',
      icon: <ProfileOutlined />,
      label: 'My CV',
      onClick: () => navigate('/my-cv'),
    },
    {
      key: 'my-favorites',
      icon: <StarOutlined />,
      label: 'My Favorites',
      onClick: () => navigate('/favorites'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      danger: true,
      onClick: logout,
    },
  ];

  return (
    <Dropdown
      menu={{ items }}
      trigger={['click', 'hover']}
      placement="bottomRight"
    >
      <Avatar
        icon={<UserOutlined />}
        style={{ cursor: 'pointer', backgroundColor: '#1677ff' }}
      />
    </Dropdown>
  );
};

export default UserMenu;