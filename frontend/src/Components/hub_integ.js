import React, { useState, useEffect } from "react";
import axios from "axios";

function HubspotIntegration() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("auth") === "success") {
      alert("✅ Authorization is complete! You can now load contacts.");

      // from the address bar it knows we concluded authorization and sends alert
      window.history.replaceState({}, document.title, "/");
    }
  }, []);

  //Starting point oauth initiation
  const startAuthorization = async () => {
    try {
      setError("");
      //Backend should return the authorization URL as text or JSON
      const res = await axios.post("http://localhost:6299/integrations/hubspot/authorize",    
        new URLSearchParams({
          user_id: "123",
          org_id: "abc"
        })
      );
      window.location.href = res.data.url;
      window.open(res.data.url, "_self"); 
    } catch (err) {
      setError("Error starting authorization.");
      console.error(err);
    }
  };

  //Getting contacts from the hubspot API endpoint
  const loadItems = async () => {
    try {
      setError("");
      setLoading(true);

      // Get credentials from backend
      const credsRes = await axios.post("http://localhost:6299/integrations/hubspot/credentials", 
        new URLSearchParams({
          user_id: "123",
          org_id: "abc"
        })
      );

      // Use credentials to load contacts
      const itemsRes = await axios.post("http://localhost:6299/integrations/hubspot/get_hubspot_items", 
        new URLSearchParams({
          credentials: JSON.stringify(credsRes.data)
        })
      );

      setItems(itemsRes.data);
    } catch (err) {
      setError("Error loading items. If you havent authorised, then pls do");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h2>HubSpot Integration</h2>
      <button onClick={startAuthorization} style={{ marginRight: "10px" }}>
        Connect HubSpot
      </button>
      <button onClick={loadItems}>Load HubSpot Contacts</button>

      {error && (
        <div style={{ color: "red", marginTop: "10px" }}>
          {error}
        </div>
      )}

      {loading && (
        <div style={{ marginTop: "10px" }}>Loading...</div>
      )}

      {items.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3>Contacts</h3>
          <table border="1" cellPadding="8" cellSpacing="0" style={{ borderCollapse: "collapse", width: "100%" }}>
      <thead style={{ background: "#f0f0f0" }}>
        <tr>
          <th>Name</th>
          <th>Contact Type</th>
          <th>Created At</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.name}</td>
            <td>{item.type}</td>
            <td>{item.creation_time ? new Date(item.creation_time).toLocaleString() : "—"}</td>
          </tr>
        ))}
      </tbody>
    </table>
        </div>
      )}
    </div>
  );
}

export default HubspotIntegration;
