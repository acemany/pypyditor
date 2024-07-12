package individualClasses;

import java.awt.event.ActionEvent;
import java.io.FileReader;
import java.io.IOException;

import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JTextArea;

public class Open extends JFrame {
	private JFileChooser fileSelect = new JFileChooser();
	private JTextArea textArea = new JTextArea(20, 60);


	Action Open = new AbstractAction("Open File") {
		  @Override
		  public void actionPerformed(ActionEvent e) {
		   if (fileSelect.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
		    openFile(fileSelect.getSelectedFile().getAbsolutePath());
		   }
		   
		  }
		    };
		    
		    public void openFile(String fileName) {
		        FileReader fr = null;
		        try {
		            fr = new FileReader(fileName);
		            textArea.read(fr, null);
		            fr.close();
		            setTitle(fileName);
		            
		        } catch (IOException e) {
		            e.printStackTrace();
		        }
		    }
		    

}
