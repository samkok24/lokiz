import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import MainLayout from "./components/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import Feed from "./pages/Feed";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import Explore from "./pages/Explore";
import Messages from "./pages/Messages";
import Notifications from "./pages/Notifications";
import Settings from "./pages/Settings";
import Search from "./pages/Search";

function Router() {
  return (
    <Switch>
      {/* Auth pages without layout */}
      <Route path="/login" component={Login} />
      <Route path="/register" component={Register} />
      
      {/* Main pages with layout */}
      <Route path="/">
        <MainLayout>
          <Feed />
        </MainLayout>
      </Route>
      
      <Route path="/explore">
        <MainLayout>
          <Explore />
        </MainLayout>
      </Route>
      
      <Route path="/search">
        <MainLayout>
          <Search />
        </MainLayout>
      </Route>
      
      <Route path="/profile/:id">
        <MainLayout>
          <Profile />
        </MainLayout>
      </Route>
      
      <Route path="/messages">
        <ProtectedRoute>
          <MainLayout>
            <Messages />
          </MainLayout>
        </ProtectedRoute>
      </Route>
      
      <Route path="/notifications">
        <ProtectedRoute>
          <MainLayout>
            <Notifications />
          </MainLayout>
        </ProtectedRoute>
      </Route>
      
      <Route path="/settings">
        <ProtectedRoute>
          <MainLayout>
            <Settings />
          </MainLayout>
        </ProtectedRoute>
      </Route>
      
      <Route path="/404" component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="dark"
        // switchable
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
