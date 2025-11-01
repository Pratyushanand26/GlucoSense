import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const ChartCard = ({ data }) => {
  if (!data || data.length === 0) {
    return <p className="text-gray-500 text-center">No data available</p>;
  }

  return (
    <div className="bg-white shadow-lg rounded-2xl p-5 mt-4">
      <h3 className="text-lg font-semibold mb-3">Glucose Levels</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Line type="monotone" dataKey="glucose" stroke="#2563EB" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ChartCard;
