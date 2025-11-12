import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import PatientDashboard from './components/PatientDashboard';
import ProviderDashboard from './components/ProviderDashboard';
import AppointmentScheduler from './components/AppointmentScheduler';
import Billing from './components/Billing';
import Notifications from './components/Notifications';

const App: React.FC = () => {
  return (
    <Router>
      <Switch>
        <Route path="/" exact component={Home} />
        <Route path="/login" component={Login} />
        <Route path="/patient-dashboard" component={PatientDashboard} />
        <Route path="/provider-dashboard" component={ProviderDashboard} />
        <Route path="/appointments" component={AppointmentScheduler} />
        <Route path="/billing" component={Billing} />
        <Route path="/notifications" component={Notifications} />
      </Switch>
    </Router>
  );
};

export default App;