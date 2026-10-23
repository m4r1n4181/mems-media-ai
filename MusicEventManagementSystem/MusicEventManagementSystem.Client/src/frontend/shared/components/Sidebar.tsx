import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  LogOut, BarChart2, Bookmark, Clock, ChevronLeft, ChevronRight, Megaphone, PieChart, Film, GitBranch, Workflow, Tag
} from "lucide-react";

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [userDepartment, setUserDepartment] = useState<number>(1);
  const navigate = useNavigate();

  useEffect(() => {
    // Get user's department from localStorage
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        setUserDepartment(user.department);
      } catch {
        // Handle parse error
      }
    }
  }, []);

  // The app is a marketing tool now: every user gets the marketing menu
  // (ticket sales, event and artist modules are no longer part of the product).
  const getMenuItems = (_department: number) => [
    { icon: <BarChart2 />, label: "Dashboard", path: "/media-campaign/dashboard" },
    { icon: <Megaphone />, label: "Campaigns", path: "/media-campaign/campaigns" },
    { icon: <Tag />, label: "Brands", path: "/media-campaign/brands" },
    { icon: <Film />, label: "Ads", path: "/media-campaign/ads" },
    { icon: <Bookmark />, label: "Ad Types", path: "/media-campaign/adtypes" },
    { icon: <Workflow />, label: "Workflows", path: "/media-campaign/workflows" },
    { icon: <PieChart />, label: "Analytics", path: "/media-campaign/analytics" },
    { icon: <GitBranch />, label: "Integrations", path: "/media-campaign/integrations" },
    { icon: <Clock />, label: "My Tasks", path: "/media-campaign/mytasks" },
  ];

  const menuItems = getMenuItems(userDepartment);

  // Highlight the item that matches the current URL (also for sub-pages such as
  // /media-campaign/campaigns/5/influencers), so the highlight survives page loads.
  const { pathname } = useLocation();
  const activeItem = menuItems.findIndex(
    (item) => pathname === item.path || pathname.startsWith(item.path + "/")
  );

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    navigate("/login");
  };

  const getDepartmentName = (department: number): string => {
    switch (department) {
      case 1: return "Ticket Sales";
      case 2: return "Event Organization";
      case 3: return "Artist Communication";
      case 4: return "Media Campaign";
      default: return "MEMS";
    }
  };

  const getDepartmentColor = (department: number): string => {
    switch (department) {
      case 1: return "lime"; // Ticket Sales
      case 2: return "pink"; // Event Organization
      case 3: return "sky"; // Artist Communication
      case 4: return "purple"; // Media Campaign
      default: return "neutral";
    }
  };

  const color = getDepartmentColor(userDepartment);

  return (
    <div
      className={`flex flex-col justify-between bg-neutral-900/80 backdrop-blur-sm border border-neutral-800 text-white h-[calc(100vh-2rem)] my-4 ml-4 rounded-2xl transition-all duration-300 shadow-2xl ${
        isOpen ? "w-64" : "w-22"
      }`}
    >
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          {isOpen && (
            <div className="transition-all duration-300">
              <div className="text-2xl font-black text-white tracking-tight">MEMS</div>
              <div className={`w-40 h-1 rounded-full mt-1 ${
                color === 'lime' ? 'bg-lime-400' :
                color === 'pink' ? 'bg-pink-400' :
                color === 'sky' ? 'bg-sky-400' :
                'bg-purple-400'
              }`}></div>
              <div className="text-xs text-neutral-400 mt-1">
                {getDepartmentName(userDepartment)}
              </div>
            </div>
          )}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className={`p-2 ml-1 hover:bg-neutral-800 rounded-xl transition-all duration-200 text-neutral-400 border border-transparent ${
              color === 'lime' ? 'hover:text-lime-400 hover:border-lime-400/30' :
              color === 'pink' ? 'hover:text-pink-400 hover:border-pink-400/30' :
              color === 'sky' ? 'hover:text-sky-400 hover:border-sky-400/30' :
              'hover:text-purple-400 hover:border-purple-400/30'
            }`}
          >
            {isOpen ? <ChevronLeft size={25} /> : <ChevronRight size={25} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {menuItems.map((item, index) => (
            <button
              key={index}
              onClick={() => {
                navigate(item.path);
              }}
              className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-200 w-full group ${
                activeItem === index
                  ? `${
                      color === 'lime' ? 'bg-lime-400/20 text-lime-400 border border-lime-400/30' :
                      color === 'pink' ? 'bg-pink-400/20 text-pink-400 border border-pink-400/30' :
                      color === 'sky' ? 'bg-sky-400/20 text-sky-400 border border-sky-400/30' :
                      'bg-purple-400/20 text-purple-400 border border-purple-400/30'
                    }`
                  : "hover:bg-neutral-800 text-neutral-400 hover:text-white"
              }`}
            >
              <div
                className={`transition-all duration-200 ${
                  activeItem === index
                    ? `${
                        color === 'lime' ? 'text-lime-400' :
                        color === 'pink' ? 'text-pink-400' :
                        color === 'sky' ? 'text-sky-400' :
                        'text-purple-400'
                      }`
                    : "text-neutral-400 group-hover:text-white"
                }`}
              >
                {item.icon}
              </div>
              {isOpen && (
                <span
                  className={`font-medium transition-all duration-200 ${
                    activeItem === index
                      ? `${
                          color === 'lime' ? 'text-lime-400' :
                          color === 'pink' ? 'text-pink-400' :
                          color === 'sky' ? 'text-sky-400' :
                          'text-purple-400'
                        }`
                      : "text-neutral-300 group-hover:text-white"
                  }`}
                >
                  {item.label}
                </span>
              )}
              {activeItem === index && (
                <div className={`ml-auto w-2 h-2 rounded-full ${
                  color === 'lime' ? 'bg-lime-400' :
                  color === 'blue' ? 'bg-pink-400' :
                  color === 'purple' ? 'bg-sky-400' :
                  'bg-purple-400'
                }`}></div>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-neutral-800">
        <button
          onClick={handleLogout}
          className={`flex items-center gap-3 p-3 hover:bg-red-950/50 rounded-xl transition-all duration-200 text-red-400 hover:text-red-300 w-full group border border-transparent hover:border-red-900/50 ${
            !isOpen ? "justify-center" : ""
          }`}
        >
          <LogOut size={20} />
          {isOpen && <span className="font-medium">Sign Out</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;