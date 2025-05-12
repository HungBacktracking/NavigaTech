import { useEffect, useState } from 'react';
import { Layout, Typography, Drawer, Tabs } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import styles from './styles.module.css';
import { MenuOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import UserMenu from '../user-menu';
import { useMobile } from '../../hooks/use-mobile';

const { Header } = Layout;
const { Title } = Typography;

const MotionHeader = motion.create(Header);

const menuItems = [
  {
    label: 'Home',
    key: 'home',
  },
  {
    label: 'Job Analysis',
    key: 'job-analysis',
  },
  {
    label: 'AI Assistant',
    key: 'ai-assistant',
  },
];

const NavBar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedKey, setSelectedKey] = useState('home');
  const [drawerVisible, setDrawerVisible] = useState(false);
  const { isMobile } = useMobile();
  const { isMobile: isTablet } = useMobile(1024);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    }
  }, []);

  useEffect(() => {
    if (!isMobile) {
      setDrawerVisible(false);
    }
  }, [isMobile]);

  useEffect(() => {
    const path = location.pathname.split('/')[1];
    const matchedItem = menuItems.find(item => item.key === path);
    setSelectedKey(matchedItem?.key || '');
  }, [location.pathname]);

  const handleMenuClick = (key: string) => {
    navigate(`/${key}`);
    if (isMobile) {
      setDrawerVisible(false);
    }
  };

  const headerVariants = {
    scrolled: {
      backdropFilter: 'blur(8px)',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.09)',
      width: isMobile ? '90%' : isTablet ? '80%' : '65%',
      maxWidth: '1400px',
      marginTop: '8px',
      borderRadius: '32px',
      transition: {
        type: "tween",
        duration: 0.5,
        ease: [0.4, 0.0, 0.2, 1],
      }
    },
    top: {
      backgroundColor: 'transparent',
      backdropFilter: 'none',
      boxShadow: 'none',
      width: '100%',
      maxWidth: '1400px',
      marginTop: 0,
      borderRadius: 0,
      transition: {
        type: "tween",
        duration: 0.5,
        ease: [0.4, 0.0, 0.2, 1],
      }
    }
  };

  return (
    <>
      <MotionHeader
        initial="top"
        animate={isScrolled ? "scrolled" : "top"}
        variants={headerVariants}
        style={{
          position: 'fixed',
          zIndex: 1000,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          left: '50%',
          transform: 'translateX(-50%)',
          padding: '0 24px',
          height: '48px'
        }}
      >
        {isMobile && (
          <MenuOutlined
            onClick={() => setDrawerVisible(true)}
            style={{ fontSize: '20px', cursor: 'pointer' }}
          />
        )}

        <div className={styles.logo}>
          <Title level={4} style={{ margin: 0 }}>
            JobTinder
          </Title>
        </div>

        <div className={styles.customMenu}>
          <Tabs
            activeKey={selectedKey}
            onChange={handleMenuClick}
            className={styles.tabs}
            items={menuItems.map((item) => ({
              label: item.label,
              key: item.key,
            }))}
          />
        </div>

        <UserMenu />
      </MotionHeader>
      <Drawer
        title="Menu"
        placement="left"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        width={250}
      >
        <div className={styles.mobileMenu}>
          {menuItems.map((item) => (
            <div
              key={item.key}
              className={`${styles.mobileMenuItem} ${selectedKey === item.key ? styles.mobileSelected : ''}`}
              onClick={() => handleMenuClick(item.key)}
              style={{
                padding: '8px 16px',
                margin: '8px 0',
                cursor: 'pointer',
                borderBottom: '1px solid #f0f0f0'
              }}
            >
              {item.label}
            </div>
          ))}
        </div>
      </Drawer>
    </>
  );
};

export default NavBar;