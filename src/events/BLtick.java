package events;

public class BLtick {
	String station;
	double amp;
	double phi;
	String date;
	int timestamp;
	
	public String getStation() {
		return station;
	}
	public void setStation(String station) {
		this.station = station;
	}
	public double getAmp() {
		return amp;
	}
	public void setAmp(double amp) {
		this.amp = amp;
	}
	public double getPhi() {
		return phi;
	}
	public void setPhi(double phi) {
		this.phi = phi;
	}
	
	public String getDate() {
		return date;
	}
	public void setDate(String date) {
		this.date = date;
	}
	public int getTimestamp() {
		return timestamp;
	}
	public void setTimestamp(int timestamp) {
		this.timestamp = timestamp;
	}

	@Override
	public String toString() {
		return "BLtick [station=" + station + ", amp=" + amp + ", phi=" + phi + ", date=" + date + "]";
	}
}
