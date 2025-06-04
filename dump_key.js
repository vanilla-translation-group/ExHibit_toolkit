let keys = [new File("key_def.bin", "wb"), new File("key.bin", "wb")];
let counter = -1;

Interceptor.attach(Module.getExportByName("kernel32.dll", "LoadLibraryExA"), {
    onEnter(args) {
        this.moduleName = args[0].readCString();
    },
    onLeave(retval) {
        if (this.moduleName != "resident.dll") return;
        let module = Process.getModuleByAddress(retval);

        let result = Memory.scanSync(module.base, module.size, "EB 0E 68 ?? ?? ?? ?? 6A 02 8B ?? E8");
        if (result.length == 0) {
            send("ERROR: stage1.1");
            return;
        }
        result = Memory.scanSync(result[0].address.sub(50), 50, "8D 4? 10");
        if (result.length == 0) {
            send("ERROR: stage1.2");
            return;
        }
        let addr = result[0].address;

        for (let i = 0; i < 10; i++) {
            let insn = Instruction.parse(addr);
            if (insn.mnemonic == "call") {
                Interceptor.attach(ptr(insn.opStr), {
                    onEnter() {
                        if (counter++ > 0) {
                            if (counter == 2) send("Keys saved to key_def.bin and key.bin");
                            return;
                        }
                        keys[counter].write(this.context.ecx.add(4).readByteArray(1028));
                        keys[counter].close();
                    }
                });
                return;
            }
            addr = insn.next;
        }
        send("ERROR: stage2");
    }
});
