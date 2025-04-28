import { useEffect, useState } from 'react';
import { Layout, Avatar, Typography, Drawer } from 'antd';
import { useLocation, useNavigate } from 'react-router-dom';
import styles from './styles.module.css';
import { MenuOutlined, UserOutlined } from '@ant-design/icons';
import { motion } from 'framer-motion';
import UserMenu from '../user-menu';

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
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
      if (window.innerWidth > 768) {
        setDrawerVisible(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleResize);
    }
  }, []);

  useEffect(() => {
    const path = location.pathname.substring(1) || 'home';
    const matchedItem = menuItems.find(item => item.key === path);
    setSelectedKey(matchedItem?.key || 'home');
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
      width: isMobile ? '90%' : '50%',
      maxWidth: '1400px',
      marginTop: '8px',
      borderRadius: '32px',
      padding: '0 24px',
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
          <div className={styles.menuItems}>
            {menuItems.map((item) => (
              <motion.div
                key={item.key}
                className={`${styles.menuItem}`}
                onClick={() => handleMenuClick(item.key)}
                whileHover={{
                  color: '#1677ff',
                  transition: { duration: 0.2, ease: 'easeInOut' }
                }}
              >
                <span className={`${selectedKey === item.key ? styles.selected : ''}`}>
                  {item.label}
                </span>
                {selectedKey === item.key && (
                  <motion.div
                    className={styles.indicator}
                    layoutId="indicator"
                    initial={false}
                  />
                )}
              </motion.div>
            ))}
          </div>
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
                padding: '12px 16px',
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