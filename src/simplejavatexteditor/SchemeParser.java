package acemany;

import arc.graphics.g2d.Draw;
import arc.math.geom.Point2;
import arc.struct.StringMap;
import arc.struct.IntMap;
import arc.struct.Seq;
import arc.util.io.Reads;
import arc.util.serialization.Base64Coder;
import mindustry.Vars;
import mindustry.content.Blocks;
import mindustry.ctype.ContentType;
import mindustry.entities.units.BuildPlan;
import mindustry.game.Schematic;
import mindustry.game.Schematic.Stile;
import mindustry.io.TypeIO;
import mindustry.io.SaveFileReader;
import mindustry.type.ItemSeq;
import mindustry.type.ItemStack;
import mindustry.world.Block;
import mindustry.world.blocks.legacy.LegacyBlock;

import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.zip.InflaterInputStream;

import static mindustry.Vars.charset;


public class ContentHandler{
    private static final int maxByteLen = 1024 * 100;
    public static Seq<LogicLink> links = new Seq<>();

    static Graphics2D currentGraphics;
    static BufferedImage currentImage;


    /*public static String fixEnc(String string) throws UnsupportedEncodingException{
        return new String(string.getBytes("windows-1251"), StandardCharsets.UTF_8);
    }*/

    public static String requirementsToString(ItemSeq itemseq){
        StringBuilder output = new StringBuilder();
        for (ItemStack itemStack : itemseq) {
            output.append(itemStack.item.name).append(": ").append(itemStack.amount).append("\n");
        }
        return output.toString();
    }

    public static Schematic parseSchematic(String text) throws IOException{
        return read(new ByteArrayInputStream(Base64Coder.decode(text)));
    }

    public Schematic parseSchematicURL(String text) throws IOException{
        return read(download(text));
    }

    public static Schematic read(InputStream input) throws IOException{
        byte[] header = {'m', 's', 'c', 'h'};
        for(byte b : header){
            int head = input.read();
            if((char)head != b){
                System.out.println("Wrong header(" + (char)head + ")!");
            }
        }

        int version = input.read();

        try(DataInputStream stream = new DataInputStream(new InflaterInputStream(input))){
            short width = stream.readShort(), height = stream.readShort();

            StringMap map = new StringMap();
            byte tags = stream.readByte();
            for(int i = 0; i < tags; i++){
                map.put(stream.readUTF(), stream.readUTF());
            }
            map.put("version", "" + version);

            IntMap<Block> blocks = new IntMap<>();
            byte length = stream.readByte();
            for(int i = 0; i < length; i++){
                String name = stream.readUTF();
                Block block = Vars.content.getByName(ContentType.block, SaveFileReader.fallback.get(name, name));
                blocks.put(i, block == null || block instanceof LegacyBlock ? Blocks.air : block);
            }

            int total = stream.readInt();
            if(total > 64 * 64) System.out.println("Schematic has too many blocks!");
            Seq<Stile> tiles = new Seq<>(total);
            for(int i = 0; i < total; i++){
                Block block = blocks.get(stream.readByte());
                int position = stream.readInt();
                Object config = TypeIO.readObject(Reads.get(stream));
                byte rotation = stream.readByte();
                if(block != Blocks.air){
                    tiles.add(new Stile(block, Point2.x(position), Point2.y(position), config, rotation));
                }
            }
            return new Schematic(tiles, map, width, height);
        }
    }

    public static InputStream download(String url){
        try{
            HttpURLConnection connection = (HttpURLConnection)new URL(url).openConnection();
            connection.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36");
            return connection.getInputStream();
        }catch(Exception e){
            throw new RuntimeException(e);
        }
    }

    public static BufferedImage previewSchematic(Schematic scheme){
        if(scheme.width > 64 || scheme.height > 64) System.out.println("Schematic cannot be larger than 64x64!");
        BufferedImage image = new BufferedImage(scheme.width * 32, scheme.height * 32, BufferedImage.TYPE_INT_ARGB);

        Draw.reset();
        Seq<BuildPlan> requests = scheme.tiles.map(t -> new BuildPlan(t.x, t.y, t.rotation, t.block, t.config));
        currentGraphics = image.createGraphics();
        currentImage = image;
        requests.each(req -> {
            req.animScale = 1f;
            req.worldContext = false;
            //req.block.drawPlanRegion(req, requests);
            Draw.reset();
        });

        //requests.each(req -> req.block.drawPlanConfigTop(req, requests));

        return image;
    }

    public static String readCompressed(byte[] data, boolean relative, Stile tile) throws IOException{
        try(DataInputStream stream = new DataInputStream(new InflaterInputStream(new ByteArrayInputStream(data)))){
            int version = stream.read();

            int bytelen = stream.readInt();
            if(bytelen > maxByteLen) throw new IOException("Malformed logic data! Length: " + bytelen);
            byte[] bytes = new byte[bytelen];
            stream.readFully(bytes);

            links.clear();

            int total = stream.readInt();

            if(version == 0){
                //old version just had links, ignore those

                for(int i = 0; i < total; i++){
                    stream.readInt();
                }
            }else{
                for(int i = 0; i < total; i++){
                    String name = stream.readUTF();
                    short x = stream.readShort(), y = stream.readShort();

                    if(relative){
                        x += tile.x;
                        y += tile.y;
                    }

                    links.add(new LogicLink(x, y, name, false));
                }
            }

            return new String(bytes, charset);
        }
    }

    public static class LogicLink{
        public boolean valid;
        public int x, y;
        public String name;

        public LogicLink(int x, int y, String name, boolean valid){
            this.x = x;
            this.y = y;
            this.name = name;
            this.valid = valid;
        }
    }
}
