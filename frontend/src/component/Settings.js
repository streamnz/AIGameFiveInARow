import React, { useState, useEffect, useContext } from 'react';
import './Settings.css';
import { AuthContext } from '../context/AuthContext';
import apiClient from '../api/apiClient';

const Settings = () => {
    const { loggedInUser } = useContext(AuthContext);
    const [walletInfo, setWalletInfo] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        if (loggedInUser) {
            fetchWalletInfo();
        }
    }, [loggedInUser]);

    const fetchWalletInfo = async () => {
        try {
            const token = localStorage.getItem('jwtToken');
            const response = await apiClient.get('/user/wallet-info', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (response.data.status === 'success') {
                setWalletInfo(response.data.wallet_info);
            }
        } catch (error) {
            console.error('Failed to fetch wallet information:', error);
        }
    };

    const connectMetamask = async () => {
        if (!window.ethereum) {
            setError('Please install MetaMask! Visit https://metamask.io to download');
            return;
        }

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            // Request MetaMask connection
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts'
            });

            if (accounts.length > 0) {
                const walletAddress = accounts[0];
                await bindWallet(walletAddress);
            }
        } catch (error) {
            console.error('Failed to connect MetaMask:', error);
            if (error.code === 4001) {
                setError('User rejected the connection request');
            } else {
                setError('Failed to connect MetaMask, please try again');
            }
        } finally {
            setLoading(false);
        }
    };

    const bindWallet = async (walletAddress) => {
        try {
            const token = localStorage.getItem('jwtToken');
            const response = await apiClient.post('/user/bind-wallet', {
                wallet_address: walletAddress,
                wallet_type: 'metamask'
            }, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.data.status === 'success') {
                setSuccess('Wallet bound successfully!');
                await fetchWalletInfo(); // Refresh wallet information
            } else {
                setError(response.data.message || 'Binding failed');
            }
        } catch (error) {
            console.error('Failed to bind wallet:', error);
            setError('Failed to bind wallet, please try again');
        }
    };

    const unbindWallet = async () => {
        if (!window.confirm('Are you sure you want to unbind your wallet?')) {
            return;
        }

        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const token = localStorage.getItem('jwtToken');
            const response = await apiClient.post('/user/unbind-wallet', {}, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.data.status === 'success') {
                setSuccess('Wallet unbound successfully!');
                await fetchWalletInfo(); // Refresh wallet information
            } else {
                setError(response.data.message || 'Unbinding failed');
            }
        } catch (error) {
            console.error('Failed to unbind wallet:', error);
            setError('Failed to unbind wallet, please try again');
        } finally {
            setLoading(false);
        }
    };

    const formatWalletAddress = (address) => {
        if (!address) return '';
        return `${address.slice(0, 6)}...${address.slice(-4)}`;
    };

    const getWalletBalance = async (address) => {
        if (!window.ethereum || !address) return '0';
        
        try {
            const balance = await window.ethereum.request({
                method: 'eth_getBalance',
                params: [address, 'latest']
            });
            // Convert Wei to ETH (1 ETH = 10^18 Wei)
            const ethBalance = parseInt(balance, 16) / Math.pow(10, 18);
            return ethBalance.toFixed(4);
        } catch (error) {
            console.error('Failed to get balance:', error);
            return '0';
        }
    };

    const [balance, setBalance] = useState('0');

    useEffect(() => {
        if (walletInfo && walletInfo.wallet_address) {
            getWalletBalance(walletInfo.wallet_address).then(setBalance);
        }
    }, [walletInfo]);

    if (!loggedInUser) {
        return (
            <div className="settings-container">
                <div className="settings-error">
                    Please login first to access the settings page
                </div>
            </div>
        );
    }

    return (
        <div className="settings-container">
            <div className="settings-header">
                <h1>Account Settings</h1>
                <p>Manage your account information and wallet settings</p>
            </div>

            <div className="settings-content">
                {/* User Information Card */}
                <div className="settings-card">
                    <h3>User Information</h3>
                    <div className="user-info-section">
                        <div className="info-item">
                            <label>Username:</label>
                            <span>{loggedInUser.username}</span>
                        </div>
                        <div className="info-item">
                            <label>Email:</label>
                            <span>{loggedInUser.email}</span>
                        </div>
                        <div className="info-item">
                            <label>Score:</label>
                            <span>{loggedInUser.score || 0}</span>
                        </div>
                    </div>
                </div>

                {/* Wallet Binding Card */}
                <div className="settings-card">
                    <h3>Wallet Settings</h3>
                    
                    {error && <div className="error-message">{error}</div>}
                    {success && <div className="success-message">{success}</div>}

                    {walletInfo && walletInfo.has_wallet_bound ? (
                        <div className="wallet-bound-section">
                            <div className="wallet-info">
                                <div className="wallet-status">
                                    <span className="status-indicator connected"></span>
                                    <span>Wallet Connected</span>
                                </div>
                                <div className="wallet-details">
                                    <div className="wallet-item">
                                        <label>Wallet Address:</label>
                                        <span className="wallet-address" title={walletInfo.wallet_address}>
                                            {formatWalletAddress(walletInfo.wallet_address)}
                                        </span>
                                    </div>
                                    <div className="wallet-item">
                                        <label>Wallet Type:</label>
                                        <span>{walletInfo.wallet_type}</span>
                                    </div>
                                    <div className="wallet-item">
                                        <label>Balance:</label>
                                        <span>{balance} ETH</span>
                                    </div>
                                    <div className="wallet-item">
                                        <label>Bind Time:</label>
                                        <span>{new Date(walletInfo.bind_time).toLocaleString()}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="wallet-actions">
                                <button 
                                    className="btn-secondary"
                                    onClick={connectMetamask}
                                    disabled={loading}
                                >
                                    {loading ? 'Rebinding...' : 'Rebind Wallet'}
                                </button>
                                <button 
                                    className="btn-danger"
                                    onClick={unbindWallet}
                                    disabled={loading}
                                >
                                    Unbind Wallet
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="wallet-unbound-section">
                            <div className="wallet-status">
                                <span className="status-indicator disconnected"></span>
                                <span>No Wallet Connected</span>
                            </div>
                            <p className="wallet-description">
                                Connect your MetaMask wallet to participate in games and earn rewards
                            </p>
                            <button 
                                className="btn-primary metamask-btn"
                                onClick={connectMetamask}
                                disabled={loading}
                            >
                                {loading ? 'Connecting...' : '🦊 Connect MetaMask'}
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Settings; 