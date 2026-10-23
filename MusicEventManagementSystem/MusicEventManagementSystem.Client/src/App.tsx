import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from "./frontend/shared/components/Layout";
import Login from "./frontend/auth/pages/Login";
import Register from "./frontend/auth/pages/Register";
import ProtectedRoute from "./frontend/shared/components/ProtectedRoute";

// Only the marketing module is shown; ticket sales, events and artist communication
// pages are still in the codebase but no longer routed.

// Media Campaign imports
import MediaCampaignDashboard from "./frontend/media-campaign/pages/Dashboard";
import MediaCampaigns from "./frontend/media-campaign/pages/Campaigns";
import Ads from "./frontend/media-campaign/pages/Ads";
import AdTypes from "./frontend/media-campaign/pages/AdTypes";
import Workflows from "./frontend/media-campaign/pages/Workflows";
// import MediaCampaignAnalytics from "./frontend/media-campaign/pages/Analytics";
import Integrations from "./frontend/media-campaign/pages/Integrations";
import MyTasks from "./frontend/media-campaign/pages/MyTasks";
import Approval from "./frontend/media-campaign/pages/Approval";
import Brands from "./frontend/media-campaign/pages/Brands";
import CampaignInfluencers from "./frontend/media-campaign/pages/CampaignInfluencers";

// Add these imports for react-toastify
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Every logged-in user works in the marketing app
const DepartmentRedirect = () =>
  localStorage.getItem('user')
    ? <Navigate to="/media-campaign/dashboard" replace />
    : <Navigate to="/login" replace />;

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Protected routes - Media Campaign*/}
        <Route path="/media-campaign/dashboard" 
          element={
            <ProtectedRoute>
              <Layout>
                <MediaCampaignDashboard />
              </Layout>
            </ProtectedRoute>
          } 
        />

         <Route path="/media-campaign/ads" 
          element={
            <ProtectedRoute>
              <Layout>
                <Ads />
              </Layout>
            </ProtectedRoute>
          } 
        />

        <Route path="/media-campaign/campaigns" 
          element={
            <ProtectedRoute>
              <Layout>
                <MediaCampaigns />
              </Layout>
            </ProtectedRoute>
          } 
        />

         <Route path="/media-campaign/adtypes" 
          element={
            <ProtectedRoute>
              <Layout>
                <AdTypes />
              </Layout>
            </ProtectedRoute>
          } 
        />

        <Route path="/media-campaign/workflows" 
          element={
            <ProtectedRoute>
              <Layout>
                <Workflows />
              </Layout>
            </ProtectedRoute>
          } 
        />
         {/*
        <Route path="/media-campaign/analytics" 
          element={
            <ProtectedRoute>
              <Layout>
                <MediaCampaignAds />
              </Layout>
            </ProtectedRoute>
          } 
        />  */}

        <Route path="/media-campaign/integrations" 
          element={
            <ProtectedRoute>
              <Layout>
                <Integrations />
              </Layout>
            </ProtectedRoute>
          } 
        /> 
        <Route path="/media-campaign/mytasks" 
          element={
            <ProtectedRoute>
              <Layout>
                <MyTasks />
              </Layout>
            </ProtectedRoute>
          } 
        /> 
        <Route path="/approval/:approvalId" element={
            <ProtectedRoute>
              <Layout>
                <Approval />
              </Layout>
            </ProtectedRoute>
          } />

        <Route path="/media-campaign/brands"
          element={
            <ProtectedRoute>
              <Layout>
                <Brands />
              </Layout>
            </ProtectedRoute>
          }
        />
        <Route path="/media-campaign/campaigns/:campaignId/influencers"
          element={
            <ProtectedRoute>
              <Layout>
                <CampaignInfluencers />
              </Layout>
            </ProtectedRoute>
          }
        />

        {/* Redirect root to dashboard */}
        <Route path="/" element={<DepartmentRedirect />} />
        
        {/* Catch all - redirect to appropriate dashboard */}
        <Route path="*" element={<DepartmentRedirect />} />
      </Routes>

      {/* Add ToastContainer here for global notifications */}
      <ToastContainer />
    </Router>
  );
}

export default App;