package listeners;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;

import com.espertech.esper.common.client.EventBean;
import com.espertech.esper.runtime.client.EPRuntime;
import com.espertech.esper.runtime.client.EPStatement;
import com.espertech.esper.runtime.client.UpdateListener;

 
    public class GeneralListener implements UpdateListener {
    	private static Logger logger = LogManager.getLogger(GeneralListener.class.getName());

        public void update(EventBean[] newData, EventBean[] oldData, EPStatement epl, EPRuntime cepRT) {

           	logger.info("Event received: " + newData[0].getUnderlying());
//        	for(EventBean event : newData)
//        	{
//                  System.out.println(" average amp " + event.get("AmpAverages['DHO'].avgamp")); // + " count " + event.get("ct"));
//        	}
        }
    }