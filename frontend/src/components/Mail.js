import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { useEscapeToMain } from "../hooks/useEscapeToMain";
import { useAuth } from "../context/AuthContext";
import { fetchOperator } from "../store/slices/operatorSlice";
import {
  fetchMail,
  fetchMailDetail,
  markMailRead,
  selectMail,
  clearSelectedMail,
  setFilters,
  clearFilters,
  selectFilteredMail,
  selectSelectedMail,
  selectMailFilters,
  selectUniqueSenders,
  selectMailLoading,
  selectMailDetailLoading,
  selectMailError,
} from "../store/slices/mailSlice";
import "./Mail.css";

const Mail = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  useEscapeToMain();

  const { operatorId, setId } = useAuth();
  const mailItems = useSelector(selectFilteredMail);
  const selectedMail = useSelector(selectSelectedMail);
  const filters = useSelector(selectMailFilters);
  const uniqueSenders = useSelector(selectUniqueSenders);
  const loading = useSelector(selectMailLoading);
  const detailLoading = useSelector(selectMailDetailLoading);
  const error = useSelector(selectMailError);

  // Load operator ID from localStorage if not set
  useEffect(() => {
    if (!operatorId) {
      setId();
    }
  }, [operatorId, setId]);

  // Load operator and mail on mount
  useEffect(() => {
    if (operatorId) {
      dispatch(fetchOperator(operatorId));
      dispatch(fetchMail(operatorId));
    }
  }, [dispatch, operatorId]);

  // Clear selection on unmount
  useEffect(() => {
    return () => {
      dispatch(clearSelectedMail());
      dispatch(clearFilters());
    };
  }, [dispatch]);

  const handleMailClick = async (mail) => {
    // Select the mail
    dispatch(selectMail(mail));

    // Fetch full details
    dispatch(fetchMailDetail(mail.id));

    // Mark as read if unread
    if (!mail.is_read) {
      dispatch(markMailRead(mail.id));
    }
  };

  const handleSenderFilterChange = (e) => {
    const value = e.target.value;
    dispatch(setFilters({ sender: value || null }));
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getMailTypeIcon = (mailType) => {
    const icons = {
      SYSTEM: "[SYS]",
      REWARD: "[RWD]",
      BATTLE_RESULT: "[BTL]",
      MISSION_UPDATE: "[MSN]",
      NPC: "[NPC]",
      OPERATOR: "[OPR]",
      CORP: "[CRP]",
    };
    return icons[mailType] || "[???]";
  };

  if (loading && mailItems.length === 0) {
    return (
      <div className="mail-container">
        <div className="mail-header">
          <h1 className="mail-title">MAIL</h1>
          <button onClick={() => navigate("/menu")} className="back-btn">
            BACK TO MENU
          </button>
        </div>
        <div className="loading-state">
          <p>LOADING MAIL...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mail-container">
        <div className="mail-header">
          <h1 className="mail-title">MAIL</h1>
          <button onClick={() => navigate("/menu")} className="back-btn">
            BACK TO MENU
          </button>
        </div>
        <div className="error-state">
          <p>Error loading mail: {error}</p>
          <button onClick={() => operatorId && dispatch(fetchMail(operatorId))}>
            RETRY
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mail-container">
      <div className="mail-header">
        <h1 className="mail-title">MAIL</h1>
        <button onClick={() => navigate("/menu")} className="back-btn">
          BACK TO MENU
        </button>
      </div>

      {/* Filter Bar */}
      <div className="mail-filter-bar">
        <div className="filter-group">
          <label className="filter-label">FILTER BY SENDER:</label>
          <select
            className="filter-select"
            value={filters.sender || ""}
            onChange={handleSenderFilterChange}
          >
            <option value="">All Senders</option>
            {uniqueSenders.map((sender) => (
              <option key={sender} value={sender}>
                {sender}
              </option>
            ))}
          </select>
        </div>
        <div className="mail-count">
          {mailItems.length} message{mailItems.length !== 1 ? "s" : ""}
        </div>
      </div>

      {/* Main Content - Two Panel Layout */}
      <div className="mail-content">
        {/* Mail List Panel */}
        <div className="mail-list-panel">
          <div className="panel-header">
            <span>INBOX</span>
          </div>
          <div className="mail-list">
            {mailItems.length === 0 ? (
              <div className="no-mail-message">
                <p>No mail to display</p>
              </div>
            ) : (
              mailItems.map((mail) => (
                <div
                  key={mail.id}
                  className={`mail-list-item ${!mail.is_read ? "unread" : ""} ${
                    selectedMail?.id === mail.id ? "selected" : ""
                  }`}
                  onClick={() => handleMailClick(mail)}
                >
                  <div className="mail-item-header">
                    <span className="mail-type-icon">
                      {getMailTypeIcon(mail.mail_type)}
                    </span>
                    {!mail.is_read && <span className="unread-indicator"></span>}
                  </div>
                  <div className="mail-item-sender">{mail.sender_name}</div>
                  <div className="mail-item-subject">{mail.subject}</div>
                  <div className="mail-item-date">{formatDate(mail.created_at)}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Mail Detail Panel */}
        <div className="mail-detail-panel">
          <div className="panel-header">
            <span>MESSAGE</span>
            {selectedMail && (
              <button
                className="close-detail-btn"
                onClick={() => dispatch(clearSelectedMail())}
                title="Close message"
              >
                X
              </button>
            )}
          </div>
          <div className="mail-detail">
            {detailLoading ? (
              <div className="detail-loading">
                <p>Loading message...</p>
              </div>
            ) : selectedMail ? (
              <div className="mail-detail-content">
                <div className="mail-detail-header">
                  <div className="detail-row">
                    <span className="detail-label">FROM:</span>
                    <span className="detail-value sender">
                      {selectedMail.sender_name}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">TYPE:</span>
                    <span className={`detail-value type-${selectedMail.mail_type?.toLowerCase()}`}>
                      {selectedMail.mail_type}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">SUBJECT:</span>
                    <span className="detail-value subject">
                      {selectedMail.subject}
                    </span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-label">DATE:</span>
                    <span className="detail-value">
                      {formatDate(selectedMail.created_at)}
                    </span>
                  </div>
                </div>
                <div className="mail-body-container">
                  <div className="mail-body">
                    {selectedMail.body || "(No message content)"}
                  </div>
                </div>
                {selectedMail.attachments &&
                  Object.keys(selectedMail.attachments).length > 0 && (
                    <div className="mail-attachments">
                      <div className="attachments-header">ATTACHMENTS</div>
                      <div className="attachments-list">
                        {Object.entries(selectedMail.attachments).map(
                          ([key, value]) => (
                            <div key={key} className="attachment-item">
                              <span className="attachment-name">{key}:</span>
                              <span className="attachment-value">
                                {JSON.stringify(value)}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  )}
              </div>
            ) : (
              <div className="no-selection">
                <p>Select a message to read</p>
                <p className="hint">Click on a mail item in the inbox</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Mail;
