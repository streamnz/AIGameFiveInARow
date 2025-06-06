import React, { useState, useContext, useEffect } from 'react';
import './Register.css';
import { parseJwt } from "./jwt_util";
import apiClient from '../interceptor/axiosConfig';
import { AuthContext } from '../context/AuthContext';

function RegisterModal({ isOpen, onClose }) {
    const { handleRegisterSuccess } = useContext(AuthContext);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [verificationCode, setVerificationCode] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [emailVerified, setEmailVerified] = useState(false);
    const [codeSent, setCodeSent] = useState(false);
    const [countdown, setCountdown] = useState(0);
    const [step, setStep] = useState(1); // 1: basic info, 2: verification

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    // 倒计时效果
    useEffect(() => {
        let timer;
        if (countdown > 0) {
            timer = setTimeout(() => setCountdown(countdown - 1), 1000);
        }
        return () => clearTimeout(timer);
    }, [countdown]);

    // 重置表单状态
    const resetForm = () => {
        setUsername('');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setVerificationCode('');
        setError('');
        setLoading(false);
        setEmailVerified(false);
        setCodeSent(false);
        setCountdown(0);
        setStep(1);
    };

    // 关闭弹窗时重置状态
    const handleClose = () => {
        resetForm();
        onClose();
    };

    // 发送验证码
    const handleSendVerificationCode = async () => {
        if (!emailRegex.test(email)) {
            setError('Please enter a valid email address');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await apiClient.post('/user/send-verification-code', {
                email: email
            });

            if (response.data.status === "success") {
                setCodeSent(true);
                setCountdown(60);
                setStep(2);
                setError('');
            } else {
                setError(response.data.message || 'Failed to send verification code');
            }
        } catch (err) {
            setError('Failed to send verification code. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // 验证邮箱验证码
    const handleVerifyCode = async () => {
        if (!verificationCode.trim()) {
            setError('Please enter the verification code');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await apiClient.post('/user/verify-email-code', {
                email: email,
                code: verificationCode
            });

            if (response.data.status === "success") {
                setError('');
                setEmailVerified(true);
                setStep(1); // 验证通过后回到step 1
            } else {
                setError('Invalid verification code. Please try again.');
            }
        } catch (err) {
            setError('Email verification failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // 注册处理
    const handleRegister = async () => {
        if (!emailVerified) {
            setError('Please verify your email first');
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);

        try {
            const response = await apiClient.post('/user/register', {
                username,
                email,
                password,
                emailVerified: true
            });

            if (response.data.status === "success") {
                const token = response.data.access_token;
                handleRegisterSuccess(token);
                handleClose();
            } else {
                setError(response.data.message || 'Registration failed');
            }
        } catch (err) {
            setError('Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // 重新发送验证码
    const handleResendCode = () => {
        setVerificationCode('');
        setCodeSent(false);
        setCountdown(0);
        handleSendVerificationCode();
    };

    // 返回上一步
    const handleBackToStep1 = () => {
        setStep(1);
        setVerificationCode('');
        setCodeSent(false);
        setCountdown(0);
        setError('');
    };

    if (!isOpen) return null;

    return (
        <div className="register-modal">
            <div className="register-content">
                {/* 关闭按钮 */}
                <button className="close-btn" onClick={handleClose}>
                    ×
                </button>

                {step === 1 && (
                    <>
                        <h2>Create Account</h2>
                        
                        <form onSubmit={(e) => e.preventDefault()}>
                            <div className="form-group">
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    placeholder="Enter your username"
                                    disabled={loading}
                                    required
                                />
                            </div>
                            
                            <div className="form-group email-group">
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="Enter your email"
                                    disabled={loading || emailVerified}
                                    required
                                />
                                <button
                                    type="button"
                                    className={`verify-btn ${!emailRegex.test(email) || emailVerified ? 'disabled' : ''}`}
                                    onClick={handleSendVerificationCode}
                                    disabled={loading || !emailRegex.test(email) || emailVerified}
                                >
                                    {emailVerified ? 'Verified' : (loading ? 'Sending...' : 'Verify Email')}
                                </button>
                            </div>
                            
                            <div className="form-group">
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter your password"
                                    disabled={loading}
                                    required
                                />
                            </div>
                            
                            <div className="form-group">
                                <input
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder="Confirm your password"
                                    disabled={loading}
                                    required
                                />
                            </div>
                            
                            {error && <div className="error">{error}</div>}
                            
                            <div className="button-group">
                                <button 
                                    type="button" 
                                    className="register-btn" 
                                    onClick={handleRegister} 
                                    disabled={loading || !emailVerified}
                                >
                                    Register
                                </button>
                            </div>
                        </form>
                    </>
                )}

                {step === 2 && (
                    <div className="verification-step">
                        <div className="verification-header">
                            <div className="email-icon">📧</div>
                            <h3>Verify Your Email</h3>
                            <p>We've sent a verification code to</p>
                            <div className="email-display">{email}</div>
                        </div>
                        
                        <div className="form-group">
                            <input
                                type="text"
                                value={verificationCode}
                                onChange={(e) => setVerificationCode(e.target.value)}
                                placeholder="Enter 6-digit verification code"
                                disabled={loading}
                                maxLength="6"
                                className="verification-input"
                            />
                        </div>

                        {error && <div className="error">{error}</div>}

                        {loading && <div className="loading-spinner"></div>}

                        <div className="verification-actions">
                            <button
                                type="button"
                                className="verify-code-btn"
                                onClick={handleVerifyCode}
                                disabled={loading || !verificationCode.trim()}
                            >
                                {loading ? 'Verifying...' : 'Verify'}
                            </button>
                        </div>

                        <div className="resend-section">
                            {countdown > 0 ? (
                                <p className="countdown-text">
                                    Resend code in {countdown}s
                                </p>
                            ) : (
                                <button
                                    type="button"
                                    className="resend-btn"
                                    onClick={handleResendCode}
                                    disabled={loading}
                                >
                                    Resend Code
                                </button>
                            )}
                        </div>

                        <div className="step-navigation">
                            <button
                                type="button"
                                className="back-btn"
                                onClick={handleBackToStep1}
                                disabled={loading}
                            >
                                ← Back to Edit Info
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default RegisterModal;
