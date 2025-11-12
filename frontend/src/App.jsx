import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/api/v1/readings?piso=1")
      .then(res => setData(res.data.data || []))
      .catch(console.error);
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">SmartFloors Dashboard</h1>
      <table className="w-full border">
        <thead><tr><th>Piso</th><th>Temp</th><th>Humedad</th><th>Energía</th></tr></thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={i}>
              <td>{r.piso}</td>
              <td>{r.temp_C}</td>
              <td>{r.humedad_pct}</td>
              <td>{r.energia_kW}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export default App;
