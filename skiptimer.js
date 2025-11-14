(function () {
  // fungsi bantu untuk ambil "React Fiber"
  function getReactFiber(el) {
    for (const key in el)
      if (key.startsWith("__reactFiber$") || key.startsWith("__reactInternalInstance$"))
        return el[key];
  }

  function getPropsFromFiber(fiber) {
    let node = fiber;
    while (node && !node.memoizedProps && !node.pendingProps) node = node.return;
    return node ? (node.memoizedProps || node.pendingProps) : null;
  }

  // cari elemen timer (biasanya class ini muncul di setiap kuis/submodul)
  const el = document.querySelector(".Quiz_quizTimer__CtmcY");
  if (!el) {
    console.log("❌ Timer tidak ditemukan di halaman ini.");
    return;
  }

  const fiber = getReactFiber(el);
  let current = fiber;
  let depth = 0;
  let found = {};

  // telusuri ke atas sampai ketemu fungsi React yang kita butuh
  while (current && depth < 20) {
    const props = getPropsFromFiber(current);
    if (props) {
      if (typeof props.onTimesOut === "function") found.onTimesOut = props.onTimesOut;
      if (typeof props.onNextSection === "function") found.onNextSection = props.onNextSection;
    }
    current = current.return;
    depth++;
  }

  if (found.onTimesOut) {
    console.log("⏱ Timer dilewati (onTimesOut dijalankan)...");
    found.onTimesOut();
  } else {
    console.log("⚠️ Tidak menemukan fungsi onTimesOut");
  }

  setTimeout(() => {
    if (found.onNextSection) {
      console.log("➡️ Lanjut ke section berikutnya...");
      found.onNextSection();
    } else {
      console.log("⚠️ Tidak menemukan fungsi onNextSection");
    }
  }, 1500);
})();
