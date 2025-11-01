import React, { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth.jsx";

import api from "../services/api";
import ChartCard from "../components/ChartCard";

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get(`/data/${user.id}`);
        setData(res.data);
      } catch (err) {
        console.error("Error fetching data:", err);
      }
    };
    if (user) fetchData();
  }, [user]);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Welcome, {user?.name}</h2>
        <button onClick={logout} className="bg-red-500 px-3 py-1 rounded text-white">
          Logout
        </button>
      </div>
      <ChartCard data={data} />
    </div>
  );
};

export default Dashboard;
