import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from 'store';

import HomePage from 'containers/HomePage';
import DashboardPage from 'containers/DashboardPage';
import LoginPage from 'containers/LoginPage';
import RegisterPage from 'containers/RegisterPage';

const App = () => {
	return (
		<Provider store={store}>
			<Router>
				<Routes>
					<Route path='/' element={<HomePage />} />
					<Route path='/dashboard' element={<DashboardPage />} />
					<Route path='/login' element={<LoginPage />} />
					<Route path='/register' element={<RegisterPage />} />
				</Routes>
			</Router>
		</Provider>
	);
};

export default App;